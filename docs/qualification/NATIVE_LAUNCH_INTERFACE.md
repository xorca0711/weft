# Native launcher observations and remaining checks

Status: **13 October 2026 — native admission/recovery observed; runtime preflight held**.
The [current diagnosis](NATIVE_RUNTIME_HOLD.md) supersedes pre-submission status
below; interface and configured-target evidence remain applicable.
This follows the [read-only Mir probe](MIR_LAUNCH_CAPABILITY_CHECK.md) and refines
the [remote architecture](../REMOTE_AUTOMATION_ARCHITECTURE.md). It maps the
reported interface for review; it is not an installed adapter or launch authority.

## Evidence and reconciliation

The owner relayed Mir's report for **05:07:22–05:07:52 UTC**, including one
environment listing at **05:07:35 UTC** and no task creation or mutation.
Root did not independently retrieve the raw schema/catalog response. The relay
and deterministic comparisons are preserved privately in ignored run records.

| Check | Result | Limit |
|---|---|---|
| Saved-environment selector | Mir reports `cloud_threads_create.environmentConfigId` in its actual schema | Admission and execution were not exercised |
| Intended target | Catalog reports `weft-pilot`, `xorca0711/weft`, setup ref `d031cef02ab4a417760bca46e90a63917d215d31`, mount `weft` | No publication, owner/workspace or configured policy fields returned |
| Full configuration version | Exact match with the preserved completed manual-worker receipt | Historical continuity, not a current account or policy observation |
| Setup revision | Exact match with the original setup record | Separate from a future qualification command's source revision |
| Account routing clue | Saved-ID prefix equals the earlier CLI routing ID | Opaque prefix semantics are unverified; this does not establish Mir's current authenticated workspace |
| Root capability | No native environment-selecting creation/listing tool exposed here | Mir's capabilities do not transfer to this local task |

The owner then supplied settings screenshots. They show `weft-pilot` and the
intended repository, internet enabled, the **Package managers** preset, **three**
additional hosts, **Only me** access, and no listed secrets or variables. A later
expanded-domain screenshot shows the full list: `europepmc.org`,
`ftp.ncbi.nlm.nih.gov`, and `www.ebi.ac.uk`. It matches the three approved hosts.
These are configured-setting observations, not worker enforcement evidence.

**Owner observations are now sufficient to prepare the bounded native trial.**
The owner confirms same-workspace picker availability and repeated manual use;
network-setting inspection is complete. Keep that identity scope explicitly
owner-attested: no independent AI-host account inspection was obtained. The
[new synthetic packet](NATIVE_SYNTHETIC_TRIAL.md) requires a live exact-target
comparison before one submission and current worker enforcement before tests.
L0/L1 runtime qualification is still pending; no network amendment is needed.

## Environment-list discrepancy and shortest resolution

The later environment-list screenshot labels sharing **비공개 (Private)** and
the repository **알 수 없는 리포지터리 (Unknown repository)**. Private is not an
Unpublished badge; that image does not establish failed publication. The unknown
repository label conflicts with the Edit screen and Mir catalog's correct mapping.

Supported read-only checks on 13 October found that GitHub CLI is authenticated
as `xorca0711`; the repository exists, is public, is not archived and has default
branch `main`. The connected GitHub app also lists an installation under `xorca0711`
and resolves `weft`. Neither connection was modified. This narrows the discrepancy
but does not prove a future cloud checkout or establish the label's cause.

No official cause or specific fix for this exact label was established by the
documentation search. A UI/mapping issue is a possibility, not a diagnosis.
Do not delete the repository/environment or reconnect an account just to clear it.

The **New chat → Work in → Cloud → Select environment** check is settled by
owner confirmation: `weft-pilot` is available and manual launches have already
been tried repeatedly. Do not repeat the picker check or manual creation. Keep
the same saved environment and use the prepared Mir-native trial to test the
missing submission path. Availability is not proof of new-worker readiness.

| Observation | Next step |
|---|---|
| Correct account/workspace and `weft-pilot` available for selection | Keep the existing environment. Review the exact native synthetic packet and intent; verify actual version/policy after admission before tests |
| Explicit Unpublished status or unavailable target with unfinished setup | Inspect the existing setup report. Fix only a demonstrated failure, run relevant setup checks, then publish/republish the same environment after scope review |
| Mapping/selection error despite correct account and connected repository | Preserve the environment and use the prepared support request. Capture the exact error; do not invent a CLI environment ID or create replacements |

Publishing fixes a demonstrated publication problem. It is not an established
fix for the separate browser-permission or CLI/durable-task mismatch. Native
delegation does not require those two optional routes to be repaired first.

## Interface mapping for a future adapter

Reported tool names below have prefix `mcp__codex_apps__` in Mir's catalog.

| Operation | Reported interface | Required treatment |
|---|---|---|
| Inspect target | `cloud_threads_list_environments({cursor?})` | Resolve exact saved configuration/repository/ref/version; listing alone does not prove identity or policy |
| Submit once | `cloud_threads_create({title, prompt, environmentConfigId, ...})` | Persist intent before one permitted call; omit computer selector `environmentId` and `cwd`. Preserve configured model/service defaults |
| Acknowledge | Description promises `threadId` and `turnId`; typed return is generic `CallToolResult` | Inspect a real successful response before mapping it. Preserve both IDs in private provider evidence. Journal acknowledgement is not completion |
| Reconcile | `cloud_threads_read({threadId, limit?, cursor?})`; thread listing also exposed | Read the same task; recorded status may lag. Missing acknowledgement holds the occurrence, never authorizes resubmission |
| Continue | `cloud_threads_send_message({threadId, prompt, ...})` | Mutating turn operation, not a status query; separate scope required |
| Stop | `cloud_threads_set_archived({threadId, archived})` describes stopping/releasing work | No dedicated cancellation interface or process guarantee established. Do not test archiving on preserved tasks |
| Schedule | `automations_create_for_aeon` reported; no environment selector | Requires a qualified coordinator; no exactly-once or PC-off dispatch guarantee established. M6 stays disabled |

Saved launcher configuration ID, runtime source-configuration ID, configuration
version and task runtime ID are distinct. Do not swap them or transform prefixes.

The reported create schema exposes no explicit version pin. Re-list immediately
before a future submission, compare the frozen version, then require the admitted
worker to check its actual version before work. This detects drift; it is not an
atomic server-side pin. A task created during a race still consumes the single
submission. Preserve it and hold; do not create a replacement.

## Settings check and runtime enforcement

The documented inspection path is **Settings → Codex Cloud → Environments →
weft-pilot → ⋯ → Edit**. Inspect the active AI-host account/workspace in the
profile menu, publication status/version if displayed, and **Internet access →
Allow domains / Additional allowed domains**. Leave settings unchanged; no save,
republish, account switch or permission change is requested.
[Official environment guide](https://learn.chatgpt.com/docs/environments/cloud-environments).

1. **Before submission:** establish current account/workspace, published target,
   configured network preset and custom hosts. Bind the observations to the exact
   reviewed prompt and occurrence. An old worker's policy is historical evidence.
2. **After an authorized task is admitted, before tests or new input retrieval:**
   inspect actual source version and current enforcement through that worker's
   supported status interface. Hold on unknown policy or drift. Do not create a
   replacement or silently accept another environment.

A not-yet-created worker cannot report enforcement. This ordering does not waive
configured-policy verification or permit launching to discover an unknown target.
One startup packet was subsequently admitted; its child held before source
retrieval/tests because current runtime status was unavailable. Do not resubmit.
Remote ownership, restart retention, usage,
cancellation and checkpoint recovery remain L2 qualification work. Drive tool
schemas alone do not establish current account/access. Choi is closed, B4 remains
held, and no native route may continue the blocked review.
