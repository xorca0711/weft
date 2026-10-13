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
existing durable worker's ID. Please identify the effective permission source
and the supported launcher for this environment type.

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
