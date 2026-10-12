# Cloud launcher qualification — 12 October 2026

Status: **read-only CLI probe passed; Weft cloud dispatch is not qualified**.
No task, schedule, network change or API spending was created by this probe.

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
2. Obtain owner approval for **one synthetic-only cloud task** once its exact
   environment and committed code are reviewable. Set one attempt. Use an
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
Do not submit a task to a guessed environment or activate another worker as a
side effect. Continue code/fixture work locally. B4 remains held independently
of launcher availability.

## Choi coordinator is a separate authority

The original coordinator's metadata was readable, but the supported messaging
call returned `thread not found`. A read-only continuity query was therefore
not delivered. Do not activate a downloaded SQLite copy or declare its held
reservation released. The private continuity prompt under
`runs/backend-handoff-20261012/CHOI_COORDINATOR_CONTINUITY.txt` is prepared for the
original coordinator. It asks for current ledger identity/ancestry and a proposed
administrative closeout only. A new private checkpoint must have its actual
contents, hash and export authorization established before upload. Scientific
retention and publication are already complete; no analysis rerun is needed.
