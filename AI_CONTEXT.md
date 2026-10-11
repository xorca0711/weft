# Agent entry point

Weft is Ravel's public automation companion. Manual Europe PMC discovery, pinned
RQ context, a paper-to-question review buffer and XML reading packets are implemented.
Unattended agents, scientific execution and Ravel export are not implemented.

- [Current state](PROGRESS.md) owns completed work and exact next steps.
- [Discovery](docs/DISCOVERY.md), [decision buffer](docs/DECISION_BUFFER.md) and
  [manual reader](docs/LOCAL_READER.md) explain implemented operations and limits.
- [Implementation plan](docs/IMPLEMENTATION_PLAN.md) owns milestones;
  [gates](docs/GATES.md) distinguish runtime checks from future scientific decisions.
- `integration/ravel.lock.json` pins source identity. Context supports all 32 RQs;
  initial search profiles cover A0/A1 only. No automatic evidence join or canonical ID.
- The owner selected local Codex with manual reading runs. No paid API or unattended
  launcher is configured. Never fabricate human review or independent replication.
- `records/` contains compact public check evidence. Raw responses, full XML,
  derived reading packets and SQLite state stay in ignored `runs/` on X:.
- The physical Ravel migration remains deferred. Do not move any worktree or run
  old analysis scripts in place. Weft's source connection is read-only.
