# Agent entry point

Weft is Ravel's public automation companion. Manual Europe PMC discovery, pinned
RQ context, a paper-to-question review buffer and XML reading packets are implemented.
Unattended agents, scientific execution and Ravel export are not implemented.
The [synthetic job controls](docs/JOB_CONTROLS.md) include a ledger and built-in
Docker fixture executor with verified local terminal receipts. One manual dot/cloud dispatch-return check passed; scientific qualification remains open.

- [Current state](PROGRESS.md) owns completed work and exact next steps.
- [Discovery](docs/DISCOVERY.md), [decision buffer](docs/DECISION_BUFFER.md) and
  [manual reader](docs/LOCAL_READER.md) explain implemented operations and limits.
- [Implementation plan](docs/IMPLEMENTATION_PLAN.md) owns milestones;
  [gates](docs/GATES.md) distinguish runtime checks from future scientific decisions.
- `integration/ravel.lock.json` pins source identity. Context supports all 32 RQs;
  initial search profiles cover A0/A1 only. No automatic evidence join or canonical ID.
- The owner selected dot coordination + Codex Cloud execution after the local
  manual-reader baseline. Start with [cloud setup](docs/CLOUD_SETUP.md), then M3
  controls and the [checkpointed manual route](docs/MANUAL_PILOT.md). Private weft-pilot is published at d031cef with 58 cloud tests and a small
  independently verified export. See records/cloud-setup-20261011.json. The small
  synthetic Drive route passed [independent cloud restore](records/cloud-drive-restore-20261011.json).
  [Manual dot delegation and SQLite checkpoint restoration](records/manual-coordinator-20261011.json) passed.
  Large outputs, retention guarantees, per-job ledger integration and numerical
  execution remain unqualified; per-job synthetic controls are documented separately.
  No paid API or unattended launcher is configured. Never fabricate human review.
- No extra local PC is required. Cloud tasks pin the reviewed Weft PR revision
  and Ravel blobs; never assume main has current implementation, or X: paths and
  authoritative SQLite state exist in fresh cloud workspaces.
- `records/` contains compact public check evidence. Raw responses, full XML,
  derived reading packets and SQLite state stay in ignored `runs/` on X:.
- Ravel's physical migration completed on 11 October 2026: `X:/GitHub/ravel`
  is the real folder and the compatibility junction is gone. Existing worktrees
  remain preserved; some historical records still contain old paths. Resolve those
  explicitly in a new adapter, never by rewriting frozen evidence.
- The [Choi source review](docs/PILOT_CHOI_REVIEW.md) and input inventory are complete
  within their stated coverage. Read the [environment recommendation](docs/EXECUTION_ENVIRONMENT.md)
  before M3/M4 work. No numerical analysis, new scientific contract or scientific worker is qualified.
- Scientific raw inputs remain in Ravel; audit PDFs/receipts are in ignored
  `runs/pilot-review-20261011-v1` on X:. The public records retain source hashes and
  locators. Weft's Ravel connection remains read-only.
