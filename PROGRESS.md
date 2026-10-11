# Current project state

## Checkpointed manual pilot preparation — 11 October 2026

The owner selected **one dot coordinator, Codex Cloud execution, and private Google
Drive checkpoints before/after each job, with explicit recovery after interruption**.
No extra PC, paid service, recurring schedule or automatic scientific dispatch is
configured. [Manual protocol](docs/MANUAL_PILOT.md) records the deployment revision.

### Confirmed

- Private **weft-pilot** is published at PR #1 exact
  `d031cef02ab4a417760bca46e90a63917d215d31`. [Setup](records/cloud-setup-20261011.json)
  passed 58 tests and 15 pinned Ravel blobs. Ravel context is
  `bfe26b876221cf6c6fa6f9b16a90cfb516b5998d`. Observed cloud capacity was 4 CPUs,
  32 GiB memory and about 29.83 GiB free disk, not contractual guarantees.
- [PR #2](https://github.com/xorca0711/weft/pull/2), stacked on PR #1, adds
  [synthetic job controls](docs/JOB_CONTROLS.md): single-ledger claims, immutable
  identities, reserved unknown outcomes, bounded Docker execution, content-verified
  receipts and archives. Commit `8e61cdf038257970fde503c975434eafde069ef9` passed
  **102 Linux tests and both CI checks**. Ordinary artifacts exclude bearer leases.
- [Actual restart recovery](records/synthetic-recovery-integration-20261011.json)
  passed after the launcher exited. New attempts save authenticated claims and
  exact source snapshots privately before Docker access. The historical test that
  lacked these materials remains held; its stopped container was not treated as
  sufficient authority to rewrite the ledger. Early runtime network status was
  unknown; later receipts explicitly observed enforcement. Frozen receipts remain.
- Private Drive [upload/readback](records/cloud-drive-20261011.json) and
  [independent fresh-cloud restoration](records/cloud-drive-restore-20261011.json)
  passed for the 48,400-byte synthetic archive. All 12 included source hashes
  matched; an absent cached_setup.sh remains unverifiable. Private locators stay
  in ignored private/cloud-artifacts.json. No sharing changes or new credentials.
- [One manual dot delegation and return](records/manual-coordinator-20261011.json)
  selected the correct environment/revision and returned the expected scientific
  hold. The dot executed SQLite across separate calls and verified a consistent
  private Drive checkpoint/restore. Workspace restart retention, Drive write-once
  storage and distributed locking are not established.
- [Numerical stack summary](records/numerical-stack-summary-20261011.json): 61
  PyPI-hash-verified wheels; Linux amd64/Python 3.12.15; deterministic sparse fixture
  passed the actual Scanpy Scrublet, seurat_v3, scale/PCA/neighbors, igraph Leiden
  and UMAP APIs under 4 GiB/4 CPUs/180 seconds/network none. The unused standalone
  Scrublet/annoy package was excluded after inspecting the official Scanpy path.
  Two fixture failures/repairs are retained. This is not a full-data memory test.

### Active work and exact next steps

1. Export/retrieve the complete numerical lock, recipe, fixture and provenance;
   verify a container-side watchdog after deliberate launcher loss. The current
   synthetic host timeout alone is not a surviving scientific watchdog.
2. Prepare and review separate Ravel metadata/sparse-loader and descriptive Choi
   contracts/adapters on `codex/weft-choi-pilot-20261011`, based on current main
   bfe26b8. Root prepared a clean sparse worktree at
   `X:/GitHub/ravel/.worktrees/weft-choi-pilot-20261011`; the cloud task owns source
   preparation. Existing Ravel edits, data and seven older worktrees are preserved.
3. Bind each manual job to its frozen contract, actual task/container, complete
   inputs/code/lock, enforced limits and private before/after checkpoints. Qualify
   that integration before biological input loading or execution. An interruption
   holds redispatch pending explicit reconciliation of the original attempt.
4. Download only reviewed public GSE145031 inputs, verify hashes/coordinates/values/
   duplicates/joins and benchmark one sparse library at a time under the metadata
   contract. Freeze the descriptive contract only after its preflight passes.
5. Run P001 Figure 1B-D as an exposed, adapted descriptive analysis. Retain QC
   denominators, all resolution sensitivities, discrepancies and absent states.
   One pooled library per condition cannot support animal-level treatment inference.
   Prepare a reviewable Ravel PR; no automatic merge, acceptance or new RQ.

### Boundaries and unfinished milestones

No biological analysis has run in Weft. Scientific flags remain false; the Ravel
runner remains the authority for a future manually qualified analysis. Large
artifact export, per-job checkpoint integration and the numerical contract remain
unqualified. Independent SQLite copies and product chat memory are not the ledger.

Completed baseline: manual discovery/dedup, pinned context for 32 RQs (initial
queries A0/A1), review buffer, XML reader and Choi main-figure/S1-S7/input audit.
[Source review](docs/PILOT_CHOI_REVIEW.md) records limitations. M1 correction/version/
recall evaluation and M2 independent screening evaluation remain open; the manual
handoff test does not complete those milestones. Choi is a known-outcome benchmark.

The [roadmap](docs/IMPLEMENTATION_PLAN.md) owns milestone exits; historical decisions
and failures remain in [DEVELOPMENT.md](DEVELOPMENT.md). Automatic scientific gate
semantics, protected policy and claim grades were not changed to make a run pass.
