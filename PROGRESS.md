# Current project state

## Documentation and integration update — 12 October 2026

The root README now maps Weft, Ravel, the dot coordinator, Codex Cloud, private
Google Drive, independent review and owner decisions. It separates code hosting,
compute, backup and scientific acceptance; no Google Cloud Platform deployment or
unattended pipeline is implied. The owner-requested export resumption was admitted after ledger reconciliation.
Two of 26 parts reached Drive before another runtime disconnect: the worker
verified part 0000 by download/hash; part 0001 readback is incomplete. Root verified
both files' sizes, destination and owner-only permissions, not their bytes.
The remaining 24 parts and transfer manifest have not been uploaded. Preserve
the existing receipt, remote IDs and partial download; reconcile before resuming
the same export. No analysis rerun or complete export is established. The current
blocker is a runtime disconnect after execution, not a renewed usage-limit refusal.
Root independently verified the descendant held checkpoint: 140,174 bytes,
SHA-256 6d8ec839… , 27 events with the exact 26-event parent prefix and the same
two scientific rows. Hashes, SQLite integrity/schema and a fresh read-only restore
passed. This verifies recovery state, not the complete scientific archive.

PR #2 was merged into PR #1's old branch after PR #1 entered main, leaving its
controls and pilot records outside main. The scoped backend-connections branch
preserves that merged history and integrates main without conflicts. A new PR
must bring these existing changes and the README diagram to main; no automatic
merge or scientific acceptance is authorized. Frozen job revisions remain pinned.

## Current stage — Figure1 executed; evidence export held — 12 October 2026

The single Choi Figure1 attempt ran under the owner-selected 8 GiB cap with
unchanged frozen methods. The worker reports exit 0, no OOM, 196.03 seconds,
2,448,296 KiB peak process RSS, terminal PID 0 and all three captured process
identities absent. The original Ravel verifier passed in the worker. Reported
post-QC cells total 11,683 (PBS 4,319; day 14 3,790; day 28 3,574); final pAT2
was absent. These results are **worker-reported, pending independent artifact
readback and scientific review**. One pooled library per condition precludes
animal-level inference. [Execution record](records/choi-figure1-execution-20261012.json).

The 105,848,914-byte evidence archive is preserved in 26 bounded parts. Automatic
approval review rejected its first upload because earlier approvals covered
different archives. At that initial rejection, no upload had succeeded. The same attempt
and slot remain EXPORT_HELD; the analysis must not be rerun. The owner subsequently approved this exact payload directly in the worker.
It rechecked the archive and 26 parts, then the cloud turn failed at its usage
limit. Complete transfer/readback remains unverified. Resume only after cloud
access returns and the same worker's per-file receipts and remote metadata are
reconciled; do not duplicate uploads. Then review receipt, QC, denominators and
figures. Scientific acceptance remains open.

Root independently verified the after-run ledger checkpoint: 136,078 bytes,
24 events, two scientific rows including the earlier metadata run, the unchanged
21-event parent prefix, SQLite schema/integrity and a fresh read-only restore.
This verifies the recorded hold and recovery history, not the unexported results.
The subsequent approval/usage-interruption checkpoint also passed independent
root byte, schema, unchanged-prefix and read-only restore checks: 26 events,
the same two scientific rows, SHA-256 9222d923… . Exact anchors are in the
execution record; approval remains valid for the same payload.
A stale coordinator database had required explicit operator recovery before
dispatch: old and restored copies were preserved, the exact worker/container
was reconciled, and a new active copy and verified before-checkpoint preceded
the single start. Its cause is unknown; restart retention is not guaranteed.

The owner-approved retirement of two audited preflight containers recovered about
4.2 GiB; source, inputs, image and evidence were preserved. Pro provides a documented
16 GiB VM. Root's previous 20 GiB host floor was a planning error; 8 GiB is the
analysis container cap. [Preparation history](records/choi-figure1-resumed-preparation-20261011.json).
Metadata remains independently verified ([record](records/choi-metadata-20261011.json)).
No new RQ, claim promotion, merge or unattended execution is authorized here.

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
  **102 Linux tests and both CI checks** (superseded by the 114-test checkpoint slice below). Ordinary artifacts exclude bearer leases.
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

- The approved network-only update is published: package-manager preset plus only
  `ftp.ncbi.nlm.nih.gov`, private visibility and d031cef source pin preserved. A
  fresh dot-delegated cloud task made one proxied HEAD: HTTP 200, 349,204,480 bytes,
  no redirects or payload. [Receipt](records/cloud-ncbi-20261011.json) separates
  root UI evidence from runtime enforcement, which the child could not verify.
- The Ravel draft adapter and two contracts are on
  `codex/weft-choi-pilot-20261011` at d779520. Worker-side GNU timeout survived a
  killed launcher; all captured processes disappeared after 7.10 seconds. Root
  review requested a summary-variable fix, adapted UMAP panels and explicit
  cross-library feature-order checks before freezing. No biological run occurred.

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

### Manual checkpoint implementation slice — 11 October 2026

The reusable ledger-only helper now performs consistent SQLite backup and strict
content/schema-verified read-only restoration with external handoff anchors.
**114 tests and validator passed**. A small actual synthetic ledger/WAL snapshot
restored without activation; [receipt](records/manual-checkpoint-integration-20261011.json)
records exact implementation/database/archive hashes and unchanged source bytes.
Restore always requires operator reconciliation. Drive transport, handoff freshness,
protected capsule transport and per-job coordinator integration remain separate;
no distributed locking/authentication or retention is inferred. Historical unknown
attempts remain held; all scientific readiness and activation gates remain false.

Windows checkpoint tests also pass (12 run, one symlink-privilege skip). Root
review corrected a test-only SQLite handle leak using explicit connection closure;
production checkpoint code was unchanged. Linux CI passed at 07c5756.

### Pilot transport and reviewed Ravel handoff

The [16 MiB synthetic transfer](records/cloud-transfer-16mib-20261011.json) passed
one upload and authenticated readback, including exact archive/payload hashes,
ZIP CRCs and owner-only permissions. Larger outputs still require complete,
checked reconstruction. The single dot coordinator created and privately backed
up a fresh manual P001 ledger with zero scientific attempts; read-only restore
passed without activation. This preparation checkpoint does not authorize a job.

Ravel [PR #149](https://github.com/xorca0711/ravel/pull/149) contains reviewed draft
contracts/source. Its full unchanged Windows governance gate passes. The initial
image lacked Git; the qualified revision and export hold are recorded above.
No biological inputs or computation have run.
