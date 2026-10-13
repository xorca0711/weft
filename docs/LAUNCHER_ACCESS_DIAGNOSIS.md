# Launcher access diagnosis — 13 October 2026

Status: **read-only diagnosis complete; automatic launch remains unqualified**.
The owner authorized permission diagnosis and CLI account/environment mapping,
with a stop before new access or deployment decisions. No task was launched.

**Update check:** the app's configured production updater reports `up_to_date`
for version `26.1007.21434`, build `13901`. Windows package inventory separately
reports `OpenAI.Codex 26.1007.2314.0`. Both the PATH CLI and plugin app-server
report `0.162.0-alpha.17.2`. A standalone `0.162.1` release is listed by the
official changelog search index but was not directly verified in the fetched
page; no applicable CLI compatibility fix is confirmed. The installed updater
has no check-only option, so no CLI update was attempted. The
[prepared support request](support/LAUNCHER_SUPPORT_REQUEST_20261013.md) preserves
these distinctions and asks for effective-policy provenance and a supported
durable-environment launcher. It has not been submitted.

## Confirmed observations

| Check | Result | Scope |
|---|---|---|
| Installed CLI | `0.162.0-alpha.17.2` | Same installed executable; no upgrade or settings override |
| `login status` and documented `account/read` | ChatGPT login; identity matches the owner's designated AI-host alias; returned plan code `prolite` | Confirms CLI identity, not the browser identity or ownership of the intended environment; no pricing/tier inference from the plan code |
| Documented `config/read`, including layers | Loaded `browser_use.origins."https://chatgpt.com".access = "allow"`; user layer provides the setting, system layer has no relevant override | This diagnostic process's configuration, not the running browser tool's effective decision |
| Documented `configRequirements/read` | `requirements = null`; no forced workspace/login configuration in the selected effective fields | No managed requirements returned to this invocation; does not exclude active desktop/session/tool policy |
| `cloud list --json --limit 20` | Exit 0; empty task list, null cursor | No task-to-environment mapping exposed |
| `codex cloud` environment picker | After loading, only `All Environments (Global)` appeared; no named environments | Picker opened read-only and exited without selecting a target or submitting a prompt |
| `cloud status` for the owner's existing synthetic worker ID | Exit 1; HTTP 404, `Invalid task ID` | The CLI did not resolve this durable worker through its supplied ID |
| Supported app task reader for that same ID | Existing `Run weft synthetic qualification` found on the durable host, idle, latest turn completed | Confirms the existing worker is still addressable through the app reader; no message or rerun |
| `codex doctor --json` | Config parses; active thread overrides explicitly `not inspected`; no desktop handshake recorded in this invocation | No effective browser-policy explanation available from this diagnostic |
| Bounded desktop log search, 12–13 October | 16 files searched; four matching lines were displayed assistant summaries, not permission-decision traces | No policy provenance recovered; this is not evidence that no override exists |

The CLI status error identifies its task route as `/backend-api/wham/tasks/…`.
That is an observed error from the supported CLI, not a private endpoint invoked
directly. The empty picker and invalid worker ID demonstrate that this CLI route
has not been mapped to the existing durable environment. They do not prove why:
product-route/version differences and account/workspace scope remain unresolved.
Do not transform the worker ID, guess an environment ID, or submit a probe job.

## Browser mismatch

The earlier browser tool explicitly denied access despite the saved allow setting,
including after restart. This diagnosis now also confirms that the documented
configuration loader reads that allow setting. It therefore narrows the issue
beyond a merely unsaved UI choice, but does not identify the effective app/tool
policy source. The denied browser was not retried or accessed indirectly.

Doctor separately warns that `computer_use.windows.always_allowed_app_ids` is
unrecognized and ignored. That is a native computer-use key, and no evidence
connects it to the browser-origin denial. It was not removed or changed.

## Stop and next action

Product troubleshooting is needed for two concrete questions:

1. Which active desktop/session/tool policy produces the browser's saved-permission
   denial while the loaded origin rule says `allow`?
2. Does this CLI version support the owner's published durable `weft-pilot`
   environment, and what supported interface exposes its account/workspace and
   environment mapping? Its picker is empty and the known app worker is rejected.

No fresh login, account switch, update, privilege change, new environment or API
deployment was attempted. Any proposed access/deployment change must be reviewed
before execution. Do not ask the owner to enable the same already-allowed setting
again. Choi remains closed; B4 remains on its independent platform hold; M6 is off.

Private account/routing details and selected diagnostics are preserved under
ignored `runs/launcher-qualification-20261013/access-diagnosis/`. No credential
file or token was read; `account/read` requested `refreshToken: false`.
No diagnostic was uploaded or sent to support.

## Supported interfaces consulted

- [Codex CLI reference](https://learn.chatgpt.com/docs/cli/reference): documented cloud picker, list/status and doctor commands.
- [Codex App Server](https://learn.chatgpt.com/docs/app-server): documented stdio initialization and read-only account/configuration/requirements methods. The subprocess was closed after those reads; no thread or inference turn was started.
- [Permissions](https://learn.chatgpt.com/docs/permissions): browser surfaces and cloud environments have controls separate from filesystem/network permission profiles.

The local investigation changes no runtime code or gate semantics. Existing
scientific and synthetic test results remain unchanged; only documentation and
offline configuration/link validation apply to this update.
