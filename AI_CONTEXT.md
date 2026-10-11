# Agent entry point

Weft is Ravel's public automation companion. Manual Europe PMC discovery, pinned
RQ context, a paper-to-question review buffer and XML reading packets are implemented.
Unattended agents, scientific execution and Ravel export are not implemented.
A [synthetic-only job ledger](docs/JOB_CONTROLS.md) is the first M3 slice; it does
not dispatch cloud jobs or verify process termination.

- [Current state](PROGRESS.md) owns completed work and exact next steps.
- [Discovery](docs/DISCOVERY.md), [decision buffer](docs/DECISION_BUFFER.md) and
  [manual reader](docs/LOCAL_READER.md) explain implemented operations and limits.
- [Implementation plan](docs/IMPLEMENTATION_PLAN.md) owns milestones;
  [gates](docs/GATES.md) distinguish runtime checks from future scientific decisions.
- `integration/ravel.lock.json` pins source identity. Context supports all 32 RQs;
  initial search profiles cover A0/A1 only. No automatic evidence join or canonical ID.
- The owner selected dot coordination + Codex Cloud execution after the local
  manual-reader baseline. Start with [cloud setup](docs/CLOUD_SETUP.md), then M3
  controls and one manual dot qualification. Private weft-pilot is published at d031cef with 58 cloud tests and a small
  independently verified export. See records/cloud-setup-20261011.json. Per-job
  controls, durable cloud artifacts and numerical execution remain unqualified.
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
  before M3/M4 work. No numerical analysis, new contract or worker is qualified.
- Scientific raw inputs remain in Ravel; audit PDFs/receipts are in ignored
  `runs/pilot-review-20261011-v1` on X:. The public records retain source hashes and
  locators. Weft's Ravel connection remains read-only.
