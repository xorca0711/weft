# One-task cloud launcher qualification — 13 October 2026

Status: **manual cloud task, isolated fixtures and result readback passed; task idle**.
The automated launcher and formal pre-submission procedure remain unqualified.
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
The owner then confirmed access was enabled and supplied both UI column views.
Read-only inspection found the saved origin config explicitly allows access, and
`codex doctor` successfully loaded that config and initialized the desktop app-server.
The diagnostic explicitly does not inspect active-thread overrides. The app
processes predate the latest config change: stale session state is plausible but
unproven. A full app restart followed by one same-tool retry is the next diagnostic.
If it still denies access, preserve the mismatch for product troubleshooting.
Do not repeatedly ask for the already-enabled setting or bypass the enforcement.
No alternate private endpoint or credential route was tried; no task was submitted.

The later owner-requested restart/retry still produced the same denial with a fresh
browser inventory. This diagnostic did not resolve access. Further agent-driven
browser attempts are held pending product troubleshooting. The owner can manually
start the already-authorized task through Work in > Cloud > weft-pilot using the
prepared prompt, then supply its link for supported task-status/result inspection.
Do not submit a duplicate: the recorded agent submission count remains zero.

## Owner-operated launch and observed readiness

The owner subsequently supplied the link to **Run weft synthetic qualification**.
Supported task inspection and continuation work for that same task. One owner
submission is observed; root made zero submissions and will not create a duplicate.
Root did not complete pre-submission environment verification or persist a
submission-intent record before the owner's launch. The procedure above therefore
has not passed end to end; the manual handoff is recorded as actually observed.

The task's configuration and configuration-version IDs match the private record
of the published `weft-pilot` environment. Its display name is owner-selected
provenance, not a runtime-reported label. Initial policy enforcement was unknown;
a bounded same-task readiness recheck subsequently reported current **enforced**
restricted policy with matching identity. No environment settings were changed.

The first pinned-source Git fetch failed with an authentication prompt before any
test invocation. A subsequent read-only diagnosis made one Git discovery request
through the existing proxy/CA route: HTTP 200, no redirect/retry or policy denial.
The earlier failure's cause remains unknown. No GitHub credential was inspected
or supplied. Root independently recovered and hash-verified the initial and v2 stop
receipts and the v3 diagnostic receipt. Private task IDs, runtime/config IDs and
exact receipts remain in ignored `runs/launcher-qualification-20261013`.

## Completed bounded result

The unchanged Git route subsequently fetched the exact frozen revision into the
fresh checkout. All **18 tests passed in one invocation**, with zero failures,
errors or skips and exit 0. No earlier phase invoked tests. The checkout was clean
before and after execution. Python was 3.12.14 on Linux x86-64.

Existing unprivileged Bubblewrap 0.12.0 supplied read-only source, private temporary
storage, separate network/PID/mount/user/UTS/IPC namespaces, no network route,
no-new-privileges and zero effective capabilities. A preflight checked those
observations before the fixture invocation. The 180-second subprocess deadline
was armed; no timeout occurred, so cancellation behavior was not exercised.
The observed invocation completed in about 0.365 seconds, with the process exited
and its launcher process group absent. This is a fixture-specific isolation check,
not qualification of arbitrary author code or the Docker scientific executor.

Root independently reconstructed the exact 98-byte log and 3,334-byte receipt
and verified their SHA-256 hashes. A second read of the same completed task returned
the identical result without dispatch. The task is idle; no further synthetic job
was launched. Prior receipts remain preserved. See the
[sanitized qualification record](../records/synthetic-cloud-task-20261013.json).

No test was rerun, source changed, dependency installed or privilege added. No
Choi/B4, Drive, live literature/data/model request, scientific analysis or schedule
was involved. Browser automation remains blocked. Explicit PR #10 control review,
a qualified automated launcher/coordinator recovery route and independent B5
evaluation remain necessary before operational adoption or recurrence.

Official references checked on 13 October:
[CLI cloud commands](https://learn.chatgpt.com/docs/cli/reference) and
[published cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments).
Documentation establishes supported interfaces, not this account's current access.
