# Agent entry point

Weft is Ravel's public automation companion. Manual Europe PMC discovery, pinned
RQ context, a paper-to-question review buffer and XML reading packets are implemented.
The bounded batch coordinator and source-bound screening pull interface are also
implemented; see [commands](docs/BATCH_SCREENING.md) and the [development test](docs/BATCH_PILOT_20261012.md).
Unattended scientific dispatch is not implemented. The checkpointed manual route
has completed one Ravel metadata run with independently verified evidence; the
separate Figure1 run has executed and its complete evidence archive passed independent
byte verification. [Scientific QC and paper comparison](docs/PILOT_CHOI_SCIENTIFIC_REVIEW.md)
are complete, with annotation/denominator limits and no new RQ proposed. Complete-output
publication and human review remain open. PROGRESS owns current status; never rerun the completed attempt.
The [synthetic job controls](docs/JOB_CONTROLS.md) include a ledger and built-in
Docker fixture executor with verified local terminal receipts. One manual dot/cloud dispatch-return check passed; scientific qualification remains open.

- [Current state](PROGRESS.md) owns completed work and exact next steps.
- Next implementation priority is the [discovery/screening backend](docs/DISCOVERY_SCREENING_BACKEND.md):
  B1 and B2 mechanics passed fixtures, a local batch and a bounded manual cloud
  handoff/restore. B3 now implements source coverage, bounded local attachments
  and separate versioned data-use/RQ proposals; see
  [the B3 interface](docs/EVIDENCE_QUALIFICATION.md). Its cached-source test held
  both proposals with six figure/two supplement entries uninspected. PR #7 at
  d95d558 subsequently passed 55 targeted tests and held-proposal recovery in the
  existing cloud worker. [B4 review](docs/B3_CLOUD_B4_REVIEW.md) is paused before
  acquisition: after owner-reported publication of europepmc.org, a fresh managed
  check still finds the same worker's old enforced policy and no supported in-place
  adoption control. The owner now authorizes one new screening-only worker in the
  updated weft-pilot environment. Its creation is blocked by browser access; the
  private launch prompt is prepared under `runs/b3-cloud-b4-review-20261012` and
  the owner was asked for the resulting task link. Verify policy and checkpoint
  restoration before review; do not substitute a default cloud environment.
  Then complete bounded source review and freeze independent screening evaluation.
  New batch reading paths are portable; older
  stores use explicit
  `batch-relocate-reading --source-root` after verified restore. See
  [cloud qualification](docs/SCREENING_CLOUD_QUALIFICATION.md): the approved host
  amendment and separate screening-only task are live.
  Cloud source/discovery, five screening responses, both owner-approved Drive
  checkpoints and independent Linux-to-Windows cached recovery passed. All stores
  are quiesced; private locators/receipts are in ignored
  `runs/screening-cloud-qualification-20261012`. No schedule is configured. Preserve
  the original Choi worker. Choi M5 publication is a separate open track, not a coding
  prerequisite. Do not enable schedules, release the held reservation or dispatch
  another live job as a side effect of this plan.
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
  The first manual metadata job has verified before/after checkpoints and Ravel
  receipt readback. A bounded 4 MiB multipart roundtrip passed; each actual archive still needs
  readback. The owner-selected 8 GiB amendment passes the memory gate. Owner-approved scoped container retirement recovered disk, and offline preflight
  passed once. Figure1 subsequently executed once. After explicit owner export
  approval and preserved interruptions, the same worker completed all 26 parts
  and the manifest. Worker and independent root reconstruction verified the exact
  105,848,914-byte archive, ZIP CRC and all 99 manifest entries. The final 30-event
  checkpoint and its three-step ancestry passed independent read-only restoration.
  No rerun, source change, network expansion or scientific acceptance occurred.
  The same reservation remains held for review. See PROGRESS.
  The after-run held checkpoint is independently verified. An explicit continuity
  recovery established a new active coordinator database; use the ignored private
  locator, not the preserved stale database. Read PROGRESS before any action.
  Retention is not guaranteed.
  No paid API or unattended launcher is configured. Never fabricate human review.
- No extra local PC is required. Cloud tasks pin the reviewed Weft PR revision
  and Ravel blobs; never assume main has current implementation, or X: paths and
  authoritative SQLite state exist in fresh cloud workspaces.
- The 12 October development store is `runs/backend-pilot-20261012-v1`; its
  private checkpoint and inactive read-only restore are adjacent ignored paths.
  It is not the Choi scientific ledger or a cloud coordinator. The public
  `records/backend-candidates-20261012.csv` lists all 74 candidates.
- B3 development copies are under ignored `runs/evidence-qualification-20261012-v1`.
  They are inactive software-test stores, not active cloud coordinators. They
  preserve the earlier cloud checkpoint and make no new source/analysis claim.
- B3 cloud receipt and exact B4 resume locators are under ignored
  `runs/b3-cloud-b4-review-20261012`. Qualification copies and the unchanged B4
  review store are quiesced. No new materials or private export were produced.
- `records/` contains compact public check evidence. Raw responses, full XML,
  derived reading packets and SQLite state stay in ignored `runs/` on X:.
- Ravel's physical migration completed on 11 October 2026: `X:/GitHub/ravel`
  is the real folder and the compatibility junction is gone. Existing worktrees
  remain preserved; some historical records still contain old paths. Resolve those
  explicitly in a new adapter, never by rewriting frozen evidence.
- The [Choi source review](docs/PILOT_CHOI_REVIEW.md) and input inventory are complete
  within their stated coverage. Read the [environment recommendation](docs/EXECUTION_ENVIRONMENT.md)
  before M3/M4 work. The frozen metadata contract and exact Git-equipped runtime
  passed one bounded metadata job; this is not full descriptive-stage qualification.
- Scientific raw inputs remain in Ravel; audit PDFs/receipts are in ignored
  `runs/pilot-review-20261011-v1` on X:. The public records retain source hashes and
  locators. Weft's Ravel connection remains read-only.
