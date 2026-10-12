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
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        if args.command == "validate":
            result = validate_project(root)
        elif args.command == "verify-ravel":
            result = verify_ravel(args.repo, read_json(root / "integration/ravel.lock.json"))
        elif args.command == "context":
            packet = build_context(args.repo, read_json(root / "integration/ravel.lock.json"), args.rq)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            write_json(args.output, packet)
            result = {"ok": True, "questions": len(packet["questions"]),
                      "catalog_sha256": packet["catalog_sha256"], "output": str(args.output)}
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
                                   overlap_days=args.overlap_days)
            result = {k: v for k, v in receipt.items() if k not in {"pages", "candidate_ids"}}
            result.update({"pages": len(receipt["pages"]), "candidates": len(receipt.get("candidate_ids", [])),
                           "receipt": str(args.store / receipt["run_id"] / "receipt.json")})
        elif args.command == "validate-reading":
            result = validate_reading(args.directory, read_json(args.assessment))
        else:
            with Store(args.store) as store:
                if args.command == "buffer-list":
                    result = {"candidates": store.candidates(), "claim_validation": False}
                elif args.command == "review-link":
                    result = store.review(args.candidate, read_json(args.record))
                elif args.command == "prepare-reading":
                    result = prepare_reading(store, args.candidate)
                else:
                    result = verify_run(store, args.run)
    except (ValidationError, OSError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 2 if result.get("status") in {"error", "truncated", "unstable", "hold"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
