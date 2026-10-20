from __future__ import annotations
import argparse
import json
from pathlib import Path
import sqlite3
import sys
from .context import build_context
from .discovery import Store, discover, stream_key, verify_run, write_json
from .validation import ValidationError, read_json, validate_project, verify_ravel
from .reading import prepare_reading, validate_reading
from . import batches, screening, qualification, handoff, intake, launches, coverage, evaluation, workflow, selection, materials, review_view, quality_review
from .identity import digest
from .reading_locations import relocate_readings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Weft discovery and read-only Ravel integration")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="Offline configuration and documentation checks")
    verify = sub.add_parser("verify-ravel", help="Verify pinned committed blobs")
    verify.add_argument("--repo", required=True, type=Path)
    context = sub.add_parser("context", help="Build source-addressed discovery context; defaults to all RQs")
    context.add_argument("--repo", required=True, type=Path)
    context.add_argument("--rq", nargs="+")
    context.add_argument("--output", required=True, type=Path)
    coverage_parser = sub.add_parser("profile-coverage", help="Audit configured queries against all pinned RQs; no retrieval or recall estimate")
    coverage_parser.add_argument("--repo", required=True, type=Path)
    evaluation_plan = sub.add_parser("evaluation-plan", help="Validate an externally reviewed evaluation plan and print its canonical JSON hash")
    evaluation_plan.add_argument("--plan", required=True, type=Path)
    evaluation_score = sub.add_parser("evaluation-score", help="Offline judgment accounting; no scientific pass or dispatch")
    evaluation_score.add_argument("--plan", required=True, type=Path)
    evaluation_score.add_argument("--plan-sha256", required=True)
    evaluation_score.add_argument("--predictions", required=True, type=Path)
    evaluation_score.add_argument("--references", required=True, type=Path)
    quality = sub.add_parser('quality-review-export', help='Private critic-to-human development review; never independent reference scoring')
    quality.add_argument('--packet', required=True, type=Path)
    quality.add_argument('--output', required=True, type=Path)
    quality.add_argument('--adjudication', type=Path, help='Explicit human response; no labels inferred')
    search = sub.add_parser("discover", help="Explicit, bounded Europe PMC metadata retrieval")
    search.add_argument("--repo", required=True, type=Path)
    search.add_argument("--profile", required=True)
    search.add_argument("--stream", default="broad")
    search.add_argument("--since", help="Initial ISO date; later runs may use the completed cutoff with overlap")
    search.add_argument("--until", required=True, help="Explicit inclusive ISO date")
    search.add_argument("--max-records", type=int, default=200)
    search.add_argument("--page-size", type=int, default=100)
    search.add_argument("--overlap-days", type=int, default=7)
    search.add_argument("--store", type=Path, default=Path("runs/discovery"))
    listing = sub.add_parser("buffer-list", help="List unvalidated paper-to-RQ candidates")
    listing.add_argument("--store", type=Path, default=Path("runs/discovery"))
    primary = sub.add_parser('paper-list', help='Source-screened primary list plus retained exclusion audit')
    primary.add_argument('--store', required=True, type=Path)
    primary.add_argument('--batch', required=True)
    review = sub.add_parser("review-link", help="Record reading priority only, never scientific acceptance")
    review.add_argument("--store", type=Path, default=Path("runs/discovery"))
    review.add_argument("--candidate", required=True)
    review.add_argument("--record", required=True, type=Path)
    receipt = sub.add_parser("verify-discovery", help="Verify locally retained discovery artifacts")
    receipt.add_argument("--store", type=Path, default=Path("runs/discovery"))
    receipt.add_argument("--run", required=True)
    reading = sub.add_parser("prepare-reading", help="Fetch one open-access XML packet for manual local Codex review")
    reading.add_argument("--store", type=Path, default=Path("runs/discovery"))
    reading.add_argument("--candidate", required=True)
    assessed = sub.add_parser("validate-reading", help="Check source hashes and locators, not semantic support")
    assessed.add_argument("--directory", required=True, type=Path)
    assessed.add_argument("--assessment", required=True, type=Path)
    batch_options = argparse.ArgumentParser(add_help=False)
    batch = batch_options
    batch.add_argument("--repo", required=True, type=Path)
    batch.add_argument("--profile", required=True)
    batch.add_argument("--streams", nargs="+", default=["broad", "rq_contrary", "adjacent_context"])
    batch.add_argument("--since", required=True)
    batch.add_argument("--until", required=True)
    batch.add_argument("--max-searches", type=int, default=12)
    batch.add_argument("--max-records", type=int, default=100)
    batch.add_argument("--max-screenings", type=int, default=5)
    batch.add_argument("--max-full-reads", type=int, default=3)
    batch.add_argument("--store", type=Path, default=Path("runs/discovery"))
    batch.add_argument('--selection-policy', choices=['legacy', 'paper-stream-v1'], help='Default: legacy for batch-discover; paper-stream-v1 for workflow-create')
    sub.add_parser("batch-discover", parents=[batch_options], help="Freeze and run a bounded discovery batch; no model launch")
    create_workflow = sub.add_parser('workflow-create', parents=[batch_options], help='Create an unstarted manual-pull workflow in a fresh store; no network')
    create_workflow.add_argument('--actor', required=True)
    selection_parser = sub.add_parser('selection-report', help='Read-only nomination/bibliography audit; no relevance or recall claim')
    selection_parser.add_argument('--store', required=True, type=Path)
    selection_parser.add_argument('--batch', required=True)
    selection_parser.add_argument('--reference', type=Path)
    selection_parser.add_argument('--include-plan', action='store_true')
    demo_parser = sub.add_parser('workflow-demo', help='Run synthetic injected transports only; write a new private demonstration directory')
    demo_parser.add_argument('--output', type=Path, required=True)
    for name in ['workflow-init', 'workflow-advance', 'workflow-status', 'workflow-submit', 'workflow-recover', 'workflow-hold', 'workflow-export', 'workflow-materials', 'workflow-import-materials', 'workflow-review-export']:
        command = sub.add_parser(name, help='Manual workflow: ' + name.removeprefix('workflow-'))
        command.add_argument('--store', required=True, type=Path)
        command.add_argument('--batch', required=True)
        if name == 'workflow-init':
            command.add_argument('--actor', required=True, help='Initialize only a fresh unstarted batch after interrupted creation')
        if name == 'workflow-advance':
            command.add_argument('--allow-network', action='store_true', help='Allow the next bounded metadata/material retrieval; never launches a model')
        if name == 'workflow-submit':
            command.add_argument('--stage', required=True, choices=['screening', 'reading', 'evidence'])
            command.add_argument('--assessment', required=True, type=Path)
        if name == 'workflow-recover':
            command.add_argument('--return-id', required=True)
        if name == 'workflow-hold':
            command.add_argument('--reason', required=True)
        if name in {'workflow-materials', 'workflow-import-materials', 'workflow-review-export'}:
            command.add_argument('--candidate', required=True)
        if name == 'workflow-import-materials':
            command.add_argument('--manifest', required=True, type=Path)
        if name == 'workflow-review-export':
            command.add_argument('--include-materials', action='store_true', help='Explicitly copy verified supplied attachments into the private bundle')
        if name in {'workflow-export', 'workflow-review-export'}:
            command.add_argument('--output', required=True, type=Path, help='New private snapshot directory; never overwrites')
    for name in ["batch-resume", "batch-relocate-reading", "batch-reconcile", "batch-next", "batch-submit", "batch-read", "batch-submit-reading", "batch-status", "batch-digest", "batch-evidence", "batch-attach-evidence", "batch-submit-evidence", "batch-evidence-status"]:
        command = sub.add_parser(name, help="Discovery batch: " + name.removeprefix("batch-"))
        command.add_argument("--store", type=Path, default=Path("runs/discovery"))
        command.add_argument("--batch", required=True)
        if name in {"batch-submit", "batch-submit-reading", "batch-submit-evidence"}:
            command.add_argument("--assessment", required=True, type=Path)
        if name == "batch-relocate-reading":
            command.add_argument("--source-root", required=True, help="Exact original store root for verified legacy path reconciliation")
        if name == "batch-status":
            command.add_argument("--include-items", action="store_true", help="Include the full candidate link list")
        if name in {"batch-read", "batch-evidence", "batch-attach-evidence", "batch-evidence-status"}:
            command.add_argument("--candidate", required=True)
        if name == "batch-attach-evidence":
            command.add_argument("--resource", required=True)
            command.add_argument("--file", required=True, type=Path)
            command.add_argument("--origin", required=True, help="Source URL/locator, recorded without fetching")
        if name == "batch-reconcile":
            command.add_argument("--window", required=True, type=int)
            command.add_argument("--reason", required=True)
    for name in ['handoff-init', 'handoff-claim', 'handoff-status', 'handoff-packet', 'handoff-submit', 'handoff-recover', 'intake-prepare', 'intake-verify']:
        command = sub.add_parser(name, help='Private cooperative screening/intake control: ' + name)
        command.add_argument('--store', type=Path, required=True)
        if name == 'handoff-claim' or name.startswith('intake-'):
            command.add_argument('--batch', required=True)
        if name == 'handoff-claim':
            command.add_argument('--actor', required=True)
            command.add_argument('--lease-seconds', type=int, default=1800)
        if name in {'handoff-packet', 'handoff-submit', 'handoff-recover'}:
            command.add_argument('--claim', required=True)
        if name == 'handoff-submit':
            command.add_argument('--assessment', type=Path, required=True)
        if name.startswith('intake-'):
            command.add_argument('--candidate', required=True)
            command.add_argument('--scope', choices=['data_review', 'rq_review'], required=True)
        if name == 'intake-verify':
            command.add_argument('--directory', type=Path, required=True)
            command.add_argument('--manifest-sha256', required=True)
    for name in ['launch-init', 'launch-prepare', 'launch-begin', 'launch-ack', 'launch-status']:
        command = sub.add_parser(name, help='Offline launch journal; no provider call: ' + name)
        command.add_argument('--journal', type=Path, required=True)
        if name in {'launch-prepare', 'launch-begin'}:
            command.add_argument('--spec', type=Path, required=True)
            command.add_argument('--prompt', type=Path, required=True)
        if name in {'launch-ack', 'launch-status'}:
            command.add_argument('--operation', required=True)
        if name == 'launch-ack':
            command.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        if args.command == "validate":
            result = validate_project(root)
        elif args.command == "verify-ravel":
            result = verify_ravel(args.repo, read_json(root / "integration/ravel.lock.json"))
        elif args.command == "profile-coverage":
            packet = build_context(args.repo, read_json(root / "integration/ravel.lock.json"))
            result = coverage.audit_profiles(read_json(root / "configs/search_profiles.json"), packet)
        elif args.command == "evaluation-plan":
            result = evaluation.validate_plan(read_json(args.plan))
        elif args.command == 'quality-review-export':
            result = quality_review.export(args.packet, args.output, read_json(args.adjudication) if args.adjudication else None)
        elif args.command == "evaluation-score":
            plan = read_json(args.plan)
            if evaluation.fingerprint(plan) != args.plan_sha256:
                raise ValidationError("Evaluation plan differs from the frozen canonical JSON hash")
            result = evaluation.evaluate(plan, read_json(args.predictions), read_json(args.references))
        elif args.command == "context":
            packet = build_context(args.repo, read_json(root / "integration/ravel.lock.json"), args.rq)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            write_json(args.output, packet)
            result = {"ok": True, "questions": len(packet["questions"]),
                      "catalog_sha256": packet["catalog_sha256"], "output": str(args.output)}
        elif args.command in {"batch-discover", 'workflow-create'}:
            from .listing import policy as listing_policy
            if args.selection_policy is None:
                args.selection_policy = 'paper-stream-v1' if args.command == 'workflow-create' else 'legacy'
            validate_project(root)
            policy = read_json(root / "configs/policy.json")
            if not 1 <= args.max_records <= policy["limits"]["records_per_search"] or not 1 <= args.max_full_reads <= policy["limits"]["full_reads_per_batch"]:
                raise ValidationError("Batch retrieval/read bound exceeds policy")
            profile = read_json(root / "configs/search_profiles.json")["profiles"][args.profile]
            packet = build_context(args.repo, read_json(root / "integration/ravel.lock.json"), profile["rq_ids"])
            coverage.validate_profile_binding(profile, packet)
            with Store(args.store) as store:
                if args.command == 'workflow-create':
                    result = workflow.create(store, packet, args.profile, profile, args.streams, args.since, args.until,
                                             actor=args.actor, max_searches=args.max_searches, max_records=args.max_records,
                                             max_screenings=args.max_screenings, max_full_reads=args.max_full_reads,
                                             selection_policy=None if args.selection_policy == 'legacy' else args.selection_policy,
                                             policy_sha=digest(policy), listing_policy=listing_policy())
                else:
                    bid = batches.create(store, packet, args.profile, profile, args.streams, args.since, args.until,
                                         max_searches=args.max_searches, max_records=args.max_records,
                                         max_screenings=args.max_screenings, max_full_reads=args.max_full_reads,
                                         selection_policy=None if args.selection_policy == 'legacy' else args.selection_policy,
                                         policy_sha=digest(policy), listing_policy=listing_policy())
                    result = batches.run(store, bid)
        elif args.command == 'selection-report':
            with workflow.readonly(args.store) as store:
                result = selection.report(store, args.batch, reference=read_json(args.reference) if args.reference else None,
                                          include_plan=args.include_plan)
        elif args.command == 'workflow-demo':
            from .demo import run
            result = run(args.output)
        elif args.command.startswith('workflow-'):
            if args.command in {'workflow-status', 'workflow-export', 'workflow-materials', 'workflow-review-export'}:
                with workflow.readonly(args.store) as store:
                    if args.command == 'workflow-status':
                        result = workflow.status(store, args.batch)
                    elif args.command == 'workflow-export':
                        result = workflow.export(store, args.batch, args.output)
                    elif args.command == 'workflow-materials':
                        result = materials.inventory(store, args.batch, args.candidate)
                    else:
                        result = review_view.export(store, args.batch, args.candidate, args.output, include_materials=args.include_materials)
            else:
                # Fail on missing/invalid stores before Store can initialize one.
                with workflow.readonly(args.store) as check:
                    if args.command == 'workflow-init':
                        batches.specification(check, args.batch)
                    else:
                        workflow._binding(check, args.batch)
                with Store(args.store) as store:
                    if args.command == 'workflow-init':
                        result = workflow.initialize(store, args.batch, args.actor)
                    elif args.command == 'workflow-advance':
                        result = workflow.advance(store, args.batch, allow_network=args.allow_network)
                    elif args.command == 'workflow-submit':
                        result = workflow.submit(store, args.batch, args.stage, read_json(args.assessment))
                    elif args.command == 'workflow-recover':
                        result = workflow.recover(store, args.batch, args.return_id)
                    elif args.command == 'workflow-import-materials':
                        result = workflow.import_materials(store, args.batch, args.candidate, args.manifest)
                    else:
                        result = workflow.hold(store, args.batch, args.reason)
        elif args.command.startswith("batch-"):
            with Store(args.store) as store:
                batches.schema(store)
                if args.command == "batch-resume":
                    result = batches.run(store, args.batch)
                elif args.command == "batch-reconcile":
                    result = batches.reconcile(store, args.batch, args.window, args.reason)
                elif args.command == "batch-relocate-reading":
                    result = relocate_readings(store, args.batch, args.source_root)
                elif args.command == "batch-next":
                    result = screening.next_packet(store, args.batch)
                elif args.command == "batch-submit":
                    result = screening.submit(store, args.batch, read_json(args.assessment))
                elif args.command == "batch-read":
                    result = screening.read_packet(store, args.batch, args.candidate)
                elif args.command == "batch-submit-reading":
                    result = screening.submit_reading(store, args.batch, read_json(args.assessment))
                elif args.command == "batch-evidence":
                    result = qualification.issue(store, args.batch, args.candidate)
                elif args.command == "batch-attach-evidence":
                    result = qualification.attach(store, args.batch, args.candidate, args.resource, args.file, args.origin)
                elif args.command == "batch-submit-evidence":
                    result = qualification.submit(store, args.batch, read_json(args.assessment))
                elif args.command == "batch-evidence-status":
                    result = qualification.summary(store, args.batch, args.candidate) or {"status":"not_prepared", "scientific_execution_allowed":False}
                elif args.command == "batch-digest":
                    result = batches.export_digest(store, args.batch)
                else:
                    result = batches.status_report(store, args.batch)
        elif args.command.startswith('launch-'):
            if args.command == 'launch-init':
                result = launches.initialize(args.journal)
            else:
                with launches.LaunchJournal(args.journal) as journal:
                    if args.command in {'launch-prepare', 'launch-begin'}:
                        with args.prompt.open('rb') as prompt_file:
                            prompt = prompt_file.read(100_001)
                        method = journal.prepare if args.command == 'launch-prepare' else journal.begin
                        result = method(read_json(args.spec), prompt)
                    elif args.command == 'launch-ack':
                        result = journal.acknowledge(args.operation, read_json(args.receipt))
                    else:
                        result = journal.status(args.operation)
        elif args.command.startswith(('handoff-', 'intake-')):
            with Store(args.store) as store:
                if args.command == 'handoff-init':
                    result = handoff.initialize(store)
                elif args.command == 'handoff-status':
                    result = handoff.status(store)
                elif args.command == 'handoff-claim':
                    result = handoff.claim(store, args.batch, args.actor, lease_seconds=args.lease_seconds)
                elif args.command == 'handoff-packet':
                    result = handoff.packet(store, args.claim)
                elif args.command == 'handoff-submit':
                    result = handoff.submit(store, args.claim, read_json(args.assessment))
                elif args.command == 'handoff-recover':
                    result = handoff.recover(store, args.claim)
                elif args.command == 'intake-prepare':
                    result = intake.prepare(store, args.batch, args.candidate, args.scope)
                else:
                    result = intake.verify(store, args.batch, args.candidate, args.scope, args.directory, args.manifest_sha256)
        elif args.command == "discover":
            validate_project(root)
            policy = read_json(root / "configs/policy.json")
            if not 1 <= args.max_records <= policy["limits"]["records_per_search"]:
                raise ValidationError("Requested retrieval exceeds the configured per-search bound")
            profiles = read_json(root / "configs/search_profiles.json")["profiles"]
            if args.profile not in profiles or args.stream not in profiles[args.profile]["streams"]:
                raise ValidationError("Unknown profile or stream; use a reviewed query in search_profiles.json")
            profile = profiles[args.profile]
            packet = build_context(args.repo, read_json(root / "integration/ravel.lock.json"), profile["rq_ids"])
            coverage.validate_profile_binding(profile, packet)
            from .listing import policy as listing_policy, scoped_profile
            profile = scoped_profile(profile, listing_policy())
            with Store(args.store) as store:
                if args.stream == "priority_journals":
                    broad_key = stream_key(profile["streams"]["broad"], profile["date_field"], packet)
                    broad = store.db.execute(
                        "SELECT id FROM runs WHERE stream_key=? AND status='complete' AND since_date<=? AND until_date>=?",
                        (broad_key, args.since or "", args.until)).fetchone()
                    if not args.since or not broad:
                        raise ValidationError("Priority search requires --since and a complete broad search covering the same window/context")
                receipt = discover(store, packet, profile["streams"][args.stream], since=args.since,
                                   until=args.until, date_field=profile["date_field"],
                                   page_size=args.page_size, max_records=args.max_records,
                                   overlap_days=args.overlap_days, listing_policy=listing_policy())
            result = {k: v for k, v in receipt.items() if k not in {"pages", "candidate_ids"}}
            result.update({"pages": len(receipt["pages"]), "candidates": len(receipt.get("candidate_ids", [])),
                           "receipt": str(args.store / receipt["run_id"] / "receipt.json")})
        elif args.command == "validate-reading":
            result = validate_reading(args.directory, read_json(args.assessment))
        else:
            with Store(args.store) as store:
                if args.command == 'paper-list':
                    from .listing import report as listing_report
                    result = listing_report(store, args.batch)
                elif args.command == "buffer-list":
                    result = {"candidates": store.candidates(), "claim_validation": False,
                              "scope": "Raw audit buffer, including exclusions; use paper-list for recommendations"}
                elif args.command == "review-link":
                    result = store.review(args.candidate, read_json(args.record))
                elif args.command == "prepare-reading":
                    result = prepare_reading(store, args.candidate)
                else:
                    result = verify_run(store, args.run)
    except (ValidationError, OSError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    if args.command.startswith("batch-") and not getattr(args, "include_items", False):
        def concise(report):
            if "items" not in report:
                return report
            from collections import Counter
            return {**{k:v for k,v in report.items() if k != "items"},
                    "item_stages":dict(Counter(i["stage"] for i in report["items"])),
                    "details":"batch-status --include-items or batch-digest"}
        result = concise(result)
        if "batch" in result:
            result["batch"] = concise(result["batch"])
    print(json.dumps(result, indent=2))
    return 2 if result.get("status") in {"error", "truncated", "unstable", "hold", "complete_with_holds"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
