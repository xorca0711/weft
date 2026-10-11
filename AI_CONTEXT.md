# Agent entry point

Project: **Weft** (`weft`), public automation companion to Ravel.
This is an initial implementation plan with a small offline validation scaffold.
No literature agent or scientific executor is implemented yet.

- [Current state](PROGRESS.md) owns handoff status.
- [Implementation plan](docs/IMPLEMENTATION_PLAN.md) owns milestones and scope.
- [Gate specification](docs/GATES.md) owns proposed transition semantics.
- [Ravel connection](docs/RAVEL_CONNECTION.md) owns repository boundaries.
- [Pilot](docs/PILOT_CHOI_2020.md) owns the first historical end-to-end target.
- `integration/ravel.lock.json` pins one Ravel revision and hashes of source files.
- `configs/` contains proposed policy, source and pilot settings. Enabled is false.
- `weft/` implements validation and read-only Git-object verification only.
- `records/` contains small public software-check records, not biological results.
- `private/`, `.env`, `data/` and `runs/` are ignored; personal interests and large
  inputs do not belong in Git. Use a separate data root with explicit provisioning.

Use repo-relative paths and configured data roots. Do not assume the historical
`scRNA_seq` path has been migrated. Do not move or modify any Ravel worktree as
part of Weft setup. A local clone containing the lock revision is sufficient
for `python -m weft verify-ravel --repo <path>`.
