# Support request: browser permission mismatch and Codex Cloud CLI compatibility

Prepared 13 October 2026. Draft only; not submitted. Account emails, account and
workspace identifiers, task/environment IDs, local usernames, credentials and
research data are omitted. The two issues below may have different causes.

## Subject

Windows ARM64: browser denies an allowed origin; CLI cannot discover a published durable cloud environment

## Summary and impact

I can manually select my published `weft-pilot` environment in the desktop app
and launch a cloud task. One synthetic task completed 18 tests successfully,
and the supported app task reader can still read it. Agent-controlled task
creation remains blocked because browser access is denied despite an allowed
origin, while the installed CLI exposes no named environments and rejects the
existing durable worker's ID. A later owner-relayed dot catalog exposes native
saved-environment delegation and the expected repository/version. A subsequent
single native creation succeeded; its child returned a preflight HOLD because
runtime instructions/current policy-status capability could not be located.
Please identify the effective browser permission source, CLI compatibility and
the supported runtime-status integration for native delegated tasks. Native
admission does not establish that the browser/CLI issues are fixed.

## Additional environment-list discrepancy

The environment list shows `weft-pilot`, an **Unknown repository** subtitle and
**Private** in the Sharing column. Private was initially mistaken for unpublished;
it is a sharing label, and that screenshot supplies no publication-status proof.
The Edit screen and the dot's environment catalog both identify `xorca0711/weft`.
The dot-reported version exactly matches an earlier manual worker's preserved receipt.

Current read-only checks resolve the public, non-archived repository through
both GitHub CLI and the connected GitHub app. CLI login and the app installation
are under `xorca0711`. These checks do not prove a cloud runtime checkout or the
cause of the contradictory environment-list label. Please clarify whether this
is stale/display metadata or a saved configuration mapping issue, and provide a
supported inspection/repair that preserves the environment and existing tasks.
No deletion, reconnection, republish or new worker was attempted to clear it.

## Installed versions and update check

Checked on 13 October 2026, approximately 04:00–04:10 UTC (13:00–13:10 KST):

- OS: Windows ARM64, reported kernel version `10.0.26200`.
- App updater: `installedVersion=26.1007.21434`, build `13901`, channel `prod`,
  status `up_to_date`. No eligible app update was offered by that checker.
- Windows package inventory: `OpenAI.Codex`, version `26.1007.2314.0`, ARM64.
  The running `ChatGPT.exe` is inside that package. These are source-specific
  version identifiers, not an assertion of two conflicting app installations.
- CLI on PATH: `codex-cli 0.162.0-alpha.17.2`, located under
  `%LOCALAPPDATA%\OpenAI\Codex\bin\<build>\codex.exe`.
- The plugin app-server executable also reports `0.162.0-alpha.17.2`.
- Installed `codex update --help` offers no check-only option. The documentation
  describes `codex update` as checking and applying an update, so it was not run.
- The official changelog search index lists standalone CLI `0.162.1`, but the
  fetched changelog page did not expose that entry for direct verification.
  Its compatibility with the app-directory CLI and applicability to these issues
  remain unverified. No CLI installer, package update or PATH change was executed.

## Issue A: saved allow rule versus browser denial

Observed sequence:

1. The owner allowed access to `https://chatgpt.com` in the app's site settings.
   Saved configuration contains:

   ```toml
   [browser_use.origins."https://chatgpt.com"]
   access = "allow"
   uploads = "allow"
   ```

2. The agent's browser tool nevertheless reported that a saved user permission
   blocks access to that origin, before it could inspect the existing tab.
3. A full app restart and one same-tool retry produced the same denial.
4. A subsequent documented read-only `config/read` with layers confirmed this
   origin rule was loaded. The user layer supplied it; the system layer had no
   relevant override. `configRequirements/read` returned `requirements: null`.
5. `codex doctor --json` says active thread overrides are `not inspected`.
   A bounded desktop log search did not recover the effective policy decision.

The configuration result belongs to a diagnostic CLI process; it does not prove
what policy the running browser tool sees. No browser retry was performed during
the latest diagnosis or update check, and no alternate route bypassed the denial.

Please explain how to inspect the active app/session/tool policy that produced
this denial and reconcile it with the saved allow rule while retaining existing
tasks and settings. Is there a known fix for this build?

## Issue B: CLI environment and worker mapping

Read-only checks with the existing CLI:

```text
codex --version
codex-cli 0.162.0-alpha.17.2

codex login status
Logged in using ChatGPT

codex cloud list --json --limit 20
{"tasks": [], "cursor": null}
```

`codex cloud` → `o` (Set Env) finished loading and displayed only
`All Environments (Global)`, with no named environment. The picker was exited
without selecting a target or submitting a task.

`codex cloud status <existing-durable-worker-id>` returned exit 1 and HTTP 404,
with `{"detail":"Invalid task ID"}`. The CLI's error showed the route
`/backend-api/wham/tasks/<existing-durable-worker-id>`. This was an error emitted
by the supported CLI; the endpoint was not called directly.

The supported app task reader resolves the exact same ID on host `durable` and
reports the existing synthetic task idle, with its last turn completed.
Documented `account/read` confirmed the CLI's intended AI-host identity without
requesting token refresh. Exact browser/CLI workspace equivalence is not proven.
No credential file or token was inspected.

Please confirm:

1. Does this CLI support the published durable environments selected through
   desktop `Work in → Cloud`, or does this command address a different task system?
2. Which supported interface lists those environments and verifies their
   account/workspace mapping before task submission?
3. Is standalone CLI `0.162.1`, another release, or an app-managed component update
   the appropriate compatibility fix? How should it be qualified alongside this
   installation without replacing the active app runtime or disrupting histories?

## Issue C: native delegated child lacks current runtime-status capability

A single native dot delegation using the exact saved `environmentConfigId` was
admitted. The coordinator reports matching catalog/version and a persisted intent
before submission, followed by an acknowledged journal reopen. Root directly
reads the resulting idle child and completed preflight-HOLD turn, and independently
verifies the original receipt/log bytes. No child source fetch or tests occurred.

The child could not locate managed-cloud instructions or a supported current
configuration/network-enforcement status interface. It performed local discovery
and MCP resource/template listing; the exposed transcript has no runtime-status
call. Its restricted `/etc/codex/network-policy.json` contains all three custom
hosts and is byte-hash-identical to the earlier successful manual worker's saved
snapshot. That does not prove current enforcement or the new worker's version.

The root's installed `cloud-environment-runtime` skill 0.1.2 describes
`cloud_environment.environment_status`, but the root catalog does not expose it.
The one authorized same-child diagnostic has now completed. The child reports
inspection of all 341 operations, all three cloud skill pages (55 skills), and
0 executor skills: no status operation, matching runtime skill or lazy tool
discovery is exposed. Status calls/retries: 0/0; no explicit access denial.
Root retrieved the completed report rather than the raw catalogs. The cause
(deployment, routing or permissions) remains unknown. No plugin was installed
or policy changed. No further diagnostic turn or replacement is being requested.

Please clarify the supported way to expose/inspect current managed-environment
status on an existing native-delegated child, including any difference from a
manually created task's runtime tool/skill injection. Can this be repaired on the
same task without recreating it? A catalog match or copied local skill must not
be represented as current enforcement. The existing task and original HOLD
evidence are preserved for diagnosis.

Separately, the task reader's `codexDelegation.input` omits one terminal LF from
the frozen worker prompt; all other text matches. Mir's relayed comparison reports
both the saved prompt and retained create argument at 4,673 UTF-8 bytes with the
original hash, versus 4,672 bytes in the XML-decoded child input without trimming.
The missing byte is the final LF at offset 4672. No raw serialized request was
retained; the earliest observable difference is argument versus child-input
representation. Please document supported prompt normalization; the responsible
layer is unknown. The original journal/spec/artifacts have not been rewritten.

Private task/turn IDs and exact hashes are prepared in a separate addendum for
this existing session. They are intentionally excluded from this public draft.
No support message has been sent. Repair of the existing integration, or an
explicitly documented equivalent runtime-status route, is the requested next
step; no policy weakening or new deployment is authorized by this report.

## Scope and available evidence

No automatic launch, permission relaxation, fresh login, account switch, update,
new API deployment or model inference was performed during diagnosis. The app
and completed cloud task remain preserved. We are asking for a supported route
that respects the effective policies.

Redacted observations are included above. Selected local diagnostics and exact
private task/environment references are retained locally, but are not attached
to this draft. Please specify the minimum additional evidence needed through an
appropriate private support channel. Full session histories are not included.

## References

- [Official troubleshooting and feedback instructions](https://learn.chatgpt.com/docs/reference/troubleshooting)
- [CLI reference](https://learn.chatgpt.com/docs/cli/reference)
- [Documented app-server account/configuration reads](https://learn.chatgpt.com/docs/app-server)
- [Official changelog](https://learn.chatgpt.com/docs/changelog)

The troubleshooting guide documents feedback through the message composer's
`/` menu and optional session sharing. This draft does not authorize sharing a
session or submitting an issue; those actions have not occurred.
