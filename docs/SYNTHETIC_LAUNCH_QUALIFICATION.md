# One-task cloud launcher qualification — 13 October 2026

Status: **authorized; not submitted; access verification blocked**.
The owner authorized verification of the intended cloud route and one synthetic-only
task in the existing `weft-pilot` environment. This supersedes the earlier pending
approval for that one task, not decisions about recurrence, paid services or new
privileges. [Launcher evidence and boundary](LAUNCHER_QUALIFICATION.md).

## Frozen task scope

| Field | Required value |
|---|---|
| Qualification ID | `weft-synthetic-launch-20261013-v1` |
| Environment | Existing published `weft-pilot`; verify current identity and policy before submission |
| Repository | `xorca0711/weft`, read-only source |
| Fixture source | `2c12090444e52108254f1c57831ecf80f239770f` (PR #10) |
| Published setup | Preserve existing setup and network settings; do not republish for this test |
| Agent tasks | One task, one attempt; no child tasks |
| Test command | `PYTHONPATH=tests python -m unittest test_handoff test_intake -q` from the pinned checkout |
| Expected result | 18 tests, zero failures/errors/skips |
| Test-process deadline | 180 seconds, enforced by the invoking subprocess or runtime; stop on timeout |
| Inputs | Checked-in synthetic fixtures and standard-library code only |
| Recovery output | Exact test log plus small JSON receipt and SHA-256 manifest; return through the task transcript |
| Excluded work | Choi, B4, live literature search, paper screening, datasets, Drive access, GitHub writes and schedules |

PR #10 controls remain under review for operational adoption. This isolated fixture
task does not merge them or authorize their use on a live screening catalog.

## Submission and recovery procedure

1. Verify the intended AI-host account/workspace, environment selection and published
   policy through an allowed supported interface. Verify repository identity separately.
   A successful empty CLI task listing does not establish these facts. Do not read,
   copy or print credentials. Unknown identity/policy keeps the task unsubmitted.
2. Save a private submission-intent record containing this qualification ID, exact
   prompt hash, source revision, verified environment reference and one-attempt limit
   **before** sending the task. Use one operator and one submission route.
3. Submit once. Save the returned task ID and acknowledgement. If the response is
   missing or ambiguous, hold and reconcile using the supported task listing/history;
   do not retry submission, switch routes or create another task. This is a manual
   duplicate-prevention procedure, not a server-side idempotency guarantee.
4. In the new worker, read applicable runtime instructions, record current enforced
   policy and verify the source revision. Obtain the exact source only through
   existing allowed access into a fresh checkout; preserve environment setup.
   If new access, dependencies or settings would be required, stop and report it.
5. Run the two existing synthetic test modules once using the runtime-required
   isolated execution route and enforced 180-second test-process timeout. No package
   installation or live discovery is required. Preserve a failing/timeout log and
   stop instead of editing tests or rerunning to obtain a pass.
6. Return exit status, test counts, timeout status, Python/runtime details and the
   source revision, plus the exact log and receipt bytes with SHA-256 hashes.
   Include observed policy provenance without credentials. The receipt must separate
   observed facts from operator instructions and unknowns. Do not claim an OS network
   boundary merely because the test adapters use fixtures.
7. Root retrieves the saved result using the same task ID, checks returned bytes and
   hashes, and reconciles source, test count and terminal status. Re-reading the same
   completed result must not dispatch or rerun anything. Preserve private routing and
   execution details in ignored `runs/`; publish only a sanitized qualification record.
8. Finish with the one task terminal and no follow-up task dispatched. Do not delete
   its evidence or alter any other worker. Preserve an unresolved task as a hold.

## What a pass establishes

One observed submission/return path to the selected environment and remote execution
of the pinned fixtures. The fixture tests exercise saved-response recovery and claim
deduplication; they do not prove cloud-submission idempotency. Transcript readback
does not prove durable workspace retention or private Drive backup recovery.

PC-off invocation by Mir, autonomous scheduling, cloud restart recovery, usage limits,
independent B5 screening quality and live scientific eligibility remain separate
qualification work. A completed synthetic task cannot unblock B4's platform hold.

## Current access evidence

On 13 October, the permitted browser tool rejected selection of the existing
ChatGPT tab: a saved user preference blocks `https://chatgpt.com`. It explicitly
forbids indirect or alternate-browser workarounds. No task submission was attempted.
The owner was asked to enable browser-control access; the task itself is already
authorized. No alternate private endpoint or credential route was tried.

Official references checked on 13 October:
[CLI cloud commands](https://learn.chatgpt.com/docs/cli/reference) and
[published cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments).
Documentation establishes supported interfaces, not this account's current access.
