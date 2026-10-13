# Backend completion review — 13 October 2026

The owner authorized bounded parallel reviews, completion of feasible partial
implementations and retries of the existing holds. Three agents reviewed
discovery, screening/evaluation and operational controls. Root integrated the
commands and reviewed discovery; the controls reviewer independently reviewed
the changed screening gates and evaluator. No scientific analysis was rerun.

## Completed software work

| Area | Change and reason | Qualification boundary |
|---|---|---|
| M1 identity | An explicit provider correction/retraction relation now holds affected current candidates whether the notice or original arrives first. Prior decisions remain in history; stale packets fail. Replay cannot silently clear the hold. | Exact provider identifiers only; provider assertions and heuristic notes remain attributed. Comments/versions are review nominations, never identity merges or scientific acceptance. Later notices must actually be retrieved. |
| M1 retrieval | Conflicting MED/PMC self-identifiers are held; malformed cursors and inconsistent hit counts cannot report a successful complete window. | Synthetic transport regression checks; no new live retrieval. |
| M1 profile coverage | `profile-coverage` audits all pinned RQs, query assignments, missing streams, draft status and exact query reuse. Thirty opt-in drafts add A2–A31 with exact source/context bindings. | All 32 RQs have configured profiles; prior retrieval evidence covers A0/A1. The 30 new profiles are draft-unqueried. Configuration coverage is not literature recall. |
| M2/B2 reading | Strict assessment/statement types and nested fields reject malformed or authority-injecting responses. A reading assessment requesting a hold returns a hold, including replay. | Structural validation and hold preservation; citation truth and scientific eligibility are not certified. |
| B5 evaluation tooling | Frozen-plan, packet and source bindings; separate reading/data/RQ metrics, missingness, disagreement, exposure strata and unblinded-reference counts. | Synthetic tests only. Owner/sample/reviewer/exposure declarations remain attestations; no independent labels or pass thresholds were invented. |
| M3b/L2 launch controls | One provider task ID cannot acknowledge two operations in the same journal. State/receipt/history inconsistencies are rejected; concurrent reads use one SQLite snapshot. | Local cooperative controls, not distributed ownership, provider idempotency or remote retention. |

The [discovery guide](DISCOVERY.md), [evaluation guide](B5_EVALUATION_PREPARATION.md)
and [launch journal](LAUNCH_INTENT_RECOVERY.md) describe usage and limits.
Each new query draft uses an existing question's terms, alternative explanations
and scope limits. Broad streams do not require the predicted effect direction;
contrary streams search alternatives without requiring an article to say its
result is negative. Adjacent contexts remain nominations. The original two
profiles are unchanged; no query, schedule or batch was launched. A selected
draft with stale source/context binding is rejected before opening a store or
retrieving metadata. Empirical relevance, provider syntax and recall remain
unqualified until a permitted bounded retrieval and independent evaluation.
Frozen cloud source and prompt bytes are unchanged; new tests are not retroactive
qualification of an older cloud packet.

## Read-only audit and offline evaluation commands

```text
python -m weft profile-coverage --repo /path/to/ravel
python -m weft evaluation-plan --plan /private/frozen-plan.json
python -m weft evaluation-score --plan /private/frozen-plan.json --plan-sha256 <retained-canonical-JSON-hash> --predictions /private/predictions.json --references /private/references.json
```

These commands emit JSON to stdout. They do not query papers, write a store,
launch a model, change a plan or grant authority. Retain the plan hash before
collecting outcomes; a changed plan needs a new version, not a replacement hash
chosen after seeing results. Examples in `tests/test_evaluation.py` are explicitly
synthetic. The metrics use frozen sample **items/packets**, potentially several
per paper, as their denominator. They are unweighted descriptive proportions,
not independent-paper accuracy, population estimates or measured search recall.
Preserve missing/disputed labels and inspect unblinded references and exposure
strata before interpreting pooled metrics.

## Hold retries and remaining sequence

| Order | Job | Current result / next dependency |
|---|---|---|
| 1 | Integrate corrected local controls | Changes and synthetic checks are reviewable; CI/merge state is recorded in PROGRESS. Choi and old run evidence remain untouched. |
| 2 | L1 native runtime qualification | One status-only follow-up to the same native task completed. It still reports 341 operations, 55 cloud skills and 0 executor skills without the supported runtime-status tool or skill. Current enforcement/version remain unknown; tests were not started. Platform integration review is required. |
| 3 | B4 material review | One status-only retry on the same held worker was again rejected by the platform's biology-content restriction. No completed status result was returned. Final material/store state remains unverified; no alternate worker, route or reformulated review was attempted. |
| 4 | M1 broader portfolio discovery | Qualify the new A2–A31 draft profiles through permitted bounded retrieval and an independent comparison bibliography. No portfolio-wide batch or material access was dispatched. First-index windows do not constitute complete monitoring of later correction feeds; no recall claim is made. |
| 5 | B3/B5 scientific qualification | Complete permitted source/material/design review, then freeze an independent sample, reference reviewers and acceptance criteria. The new evaluator computes accounting once real reviewed inputs exist; it cannot create independence or a human disposition. |
| 6 | L2/L3 remote operation | After runtime access is resolved, qualify an authoritative coordinator, same-task interruption/cancellation recovery, durable checkpoints, resource limits and operation without a PC callback. A new state service or deployment needs an owner decision. |
| 7 | L4/M6 recurrence | Only after technical and quality qualification: decide cadence, time zone, scope, usage limits, notifications and a bounded export policy. Scheduling remains disabled. |

No new cloud worker, access grant, environment edit, credential, upload, support
message or schedule was created. Choi's M4/M5 descriptive benchmark and final
administrative release remain complete. The broad milestones retain partial or
held status where their exit requirements are unmet; software fixtures do not
replace scientific validation or platform enforcement evidence.

Private retry transcripts and configuration audit are retained under ignored
`runs/roadmap-completion-20261013/`. Public status excludes worker IDs, account
details, paths to private artifacts and Drive locators.
