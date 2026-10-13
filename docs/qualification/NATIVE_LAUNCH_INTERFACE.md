# Native launcher observations and remaining checks

Status: **13 October 2026 — L0 partial; no native submission**.
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

**L0 remains unqualified.** Missing pre-launch evidence: current AI-host
account/workspace and current publication status. The network-setting inspection
is complete; no network amendment is needed. The owner has been asked to inspect
the remaining fields without changing them.

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
No startup packet has been dispatched. Remote ownership, restart retention, usage,
cancellation and checkpoint recovery remain L2 qualification work. Drive tool
schemas alone do not establish current account/access. Choi is closed, B4 remains
held, and no native route may continue the blocked review.
