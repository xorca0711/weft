# Cloud launcher qualification — 12 October 2026

Status: **read-only CLI probe passed; Weft cloud dispatch is not qualified**.
No task, schedule, network change or API spending was created by this probe.

**13 October update:** the owner authorized one synthetic-only task after access
verification. Its [frozen scope and submission procedure](SYNTHETIC_LAUNCH_QUALIFICATION.md)
are prepared. The browser still rejects `chatgpt.com`, but read-only inspection
confirmed the saved origin config explicitly allows access. The owner also confirmed
the setting. A full app restart/recheck is the next diagnostic; active-thread policy
is not inspected by `codex doctor`. The subsequent owner-requested restart/retry
also returned the denial; do not repeat it without a relevant change. No task has
been submitted. Task approval is satisfied; the prepared prompt supports a manual
owner launch followed by task-link verification through permitted task tools.

## Observed evidence

The official [Codex CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
documents the experimental `codex cloud` commands. `cloud exec` accepts a target
environment and task prompt; `cloud list --json` lists tasks. This provides a
documented interface to investigate instead of assuming browser automation is
the only possible launcher.

The installed `codex-cli 0.162.0-alpha.17.2` exposes `cloud exec`, `status`, `list`,
`diff` and `apply`. Local help reports `exec --env`, `--branch`, and `--attempts`
(default one). The authenticated `cloud list --json --limit 1` probe exited zero
and returned `tasks: []`, with no next cursor. It did not establish a visible
`weft-pilot` environment, an account/workspace match or access to the existing
desktop durable workers. Do not equate those product routes.

Separately, the official [Agents API overview](https://developers.openai.com/api/docs/guides/agents-api/overview)
describes managed sessions and hosted environments. Moving to that API is a new
deployment/authentication/spending decision, not an implied use of the current
subscription or a fallback permission.

## Recommended qualification sequence

1. Verify the intended AI-host account/workspace and `weft-pilot` environment
   through the documented CLI/product interface. Do not inspect/copy tokens or
   assume an AI-host login establishes GitHub/Drive identity.
2. Use the **one synthetic-only cloud task** authorized on 13 October once its exact
   environment is verified, at the pinned committed code. Set one attempt. Use an
   isolated fixture catalog, with no B4 source, Choi ledger, external dataset,
   Drive upload, production queue or scientific execution.
3. Record submission identity, status, bounded completion and recovery of its
   result. Prove duplicate-trigger handling and the unknown-submission case:
   a lost acknowledgement must hold rather than submit another task.
4. Verify that the selected dot can invoke the supported launcher and recover
   state while the local PC is off. A locally installed CLI alone does not
   establish this. Verify independent retention and usage controls separately.
5. Only after that qualification select an unattended host/trigger. A different
   environment, API service, credential, paid runtime or recurring schedule needs
   its own concrete deployment decision.

**Current stop:** the CLI listing establishes no route to the intended environment.
A read-only check through the existing ChatGPT browser tab was then rejected by
the browser's saved user permission for `chatgpt.com`. No alternate browser,
endpoint or indirect route was attempted. That permission must be resolved
before this browser can verify the environment. The later read-only config check
found `access = "allow"`, so the unresolved issue is the saved-config/effective-policy
discrepancy, not a missing owner approval or a demonstrated saved deny.
Do not submit a task to a guessed environment or activate another worker as a
side effect. Continue code/fixture work locally. B4 remains held independently
of launcher availability.

## Choi coordinator is a separate authority

The coordinator is **Mir**, as named in Weft's root backend map. Its durable
record has no separate chat title. `Verify Weft network access` is the cloud
worker, not the coordinator. The original coordinator's metadata was readable, but the supported messaging
call returned `thread not found`. The owner relayed the continuity request to Mir
and returned its successful read-only report: 30 events, two scientific attempts
and the held reservation. The live database and backup match logically; their
different SQLite byte hashes are explicitly preserved. Root then retrieved a
fresh original-worker check at 23:01:33 KST on 12 October: matching runtime,
original container exited with code 0/no OOM/PID 0, and captured processes absent
within the observed namespace. These are point-in-time observations, not release authority.

Do not activate a downloaded SQLite copy or infer new-job authority from closeout.
The owner subsequently approved the exact 148,366-byte administrative checkpoint
export and returned Mir's one-upload receipt. Root independently verified Drive
identity/owner-only metadata, downloaded the stored bytes, checked archive and
member hashes/CRC, then restored read-only and compared the verified parent:
31 events, exact 30-event prefix, unchanged two attempts, same identity/source/schema,
and the administrative event explicitly retaining HELD/no scientific acceptance.
No restored ledger was activated. The owner separately approved release and the
exact final export. Root independently downloaded the 156,558-byte final archive
from the verified owner-only Drive folder and passed archive/member hashes, CRC,
source/schema/parent checks and a fresh inactive read-only restore. Its 32 events
preserve the exact 31-event prefix and both scientific rows. The single release
event covers only the completed Figure1 reservation; scientific acceptance,
new-job authorization and automatic dispatch remain false.

**Administrative closeout is complete and remotely preserved.** The release
event's pre-upload preservation status is historical. Separate final download
and restore receipts establish current preservation without rewriting the event
or appending another checkpoint cycle. Root verified downloaded checkpoints,
not a new inspection of the remote live database. Private receipts are under
`runs/backend-handoff-20261012`. Direct Mir messaging remains unavailable, but no
further message, ledger change or export is required for this closeout. Scientific
retention and publication are complete within their bounded descriptive scope.
