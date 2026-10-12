# Checkpointed manual pilot

Owner-selected deployment revision, 11 October 2026. One dot coordinates manually
dispatched Codex Cloud jobs. Private Google Drive stores verified checkpoints
before and after each job. An interruption requires explicit recovery; it never
authorizes a second dispatch. This route needs no extra local PC or new service.

[Qualification evidence](../records/manual-coordinator-20261011.json) records an
actual dot/cloud round trip and a consistent SQLite backup, upload, download and
read-only restore. These are bounded synthetic checks. They do not establish
workspace restart retention, Drive immutability, a distributed lock or automatic
scientific execution. The Ravel research runner remains the scientific authority.

## Manual dispatch protocol to implement and qualify

1. Select one coordinator and one authoritative ledger identity. Record the exact
   reviewed Weft/Ravel revisions, source context, contract, input/code/environment
   hashes, allowed stage, budget and unique attempt. No other coordinator dispatches.
2. Before dispatch, make a consistent SQLite backup and preserve the exact source,
   private recovery material and immutable packet. Hash the checkpoint; upload to
   the owner-only folder with a unique name; verify metadata and downloaded bytes.
   Keep the hash anchor and locator in the operator handoff outside the archive.
   Failure or uncertain upload holds dispatch; reconcile before retrying.
3. Dispatch only the declared stage. Bind the actual cloud task and container to
   that attempt. Ravel preflight, a committed frozen contract and input/code hashes
   precede any biological computation. Use read-only source/input mounts, isolated
   output, enforced resources and a container-side watchdog that survives a lost
   host launcher. No historical analysis path may be overwritten.
4. Collect and verify Ravel receipts, terminal state, process disappearance and
   output hashes. Export outputs and a new consistent ledger checkpoint; retrieve
   and verify both before calling the manual stage complete. Runtime completion is
   separate from scientific interpretation and acceptance.
5. If interrupted, hold the attempt and its slot. An operator must select the last
   verified checkpoint and reconcile the original task/container before resuming.
   Never restore an older snapshot and interpret an absent row as permission to
   rerun. A lost container or missing authenticated recovery material stays held.

Only the synthetic APIs currently implement job execution and recovery. This
protocol is not yet a scientific dispatch API, and current policy flags remain
false. Private capsules contain bearer lease material: keep them out of ordinary
artifacts, public Git, logs and receipts. Drive access must remain owner-only.

## P001 boundary

Start with input/sparse-loader qualification under a new Ravel metadata contract,
then a separately frozen descriptive Fig. 1B-D contract. One pooled library per
condition supports library descriptions, not animal-level treatment inference.
Known D1/D2/D2b outcomes remain exposed. Preserve failed runs, absent states and
all method differences; no automatic claim promotion, new RQ, merge or schedule.

Before the first real dispatch, qualify the numerical lock, persistent watchdog,
manual per-job checkpoint/receipt integration and current Ravel contract. The
[roadmap](IMPLEMENTATION_PLAN.md) and [current state](../PROGRESS.md) own progress.

## Implemented ledger-only checkpoint helper

`weft.checkpoints.create_checkpoint` uses SQLite's backup API, including committed
WAL state, into a fresh private staging directory. It closes and integrity-checks
that standalone database against an operator-selected exact schema hash. The
canonical manifest binds a unique checkpoint ID, ledger identity, exact job/attempt
or stage reference, before-dispatch/after-run phase, optional parent archive hash,
40-character source revision, UTC timestamp and database bytes/hash. The ZIP has
exactly `ledger.sqlite` and `checkpoint-manifest.json`; recovery capsules and
bearer tokens are excluded and require separate protected transport.

`restore_checkpoint` requires the archive SHA-256, ledger identity and schema hash
from the trusted handoff outside the archive. It bounds archive/member expansion,
checks canonical metadata, CRC, database hash, integrity and schema before creating
the requested fresh directory. Duplicate/unexpected names (including traversal),
symlinks, special/encrypted members and reused destinations are rejected. It opens
the verified SQLite file read-only and returns
`REQUIRES_OPERATOR_RECONCILIATION`: it never constructs an active JobLedger,
releases a slot, launches a job or authorizes redispatch. Preserve incomplete
staging/restoration failures for inspection; do not promote them into checkpoints.

Example operator-side Python calls (transport is separate):

```python
from weft.checkpoints import create_checkpoint, restore_checkpoint
saved = create_checkpoint(
    source, fresh_staging, ledger_identity=trusted_ledger_id,
    reference={"job_id": exact_job_sha256, "attempt_id": exact_attempt},
    phase="before-dispatch", source_revision=reviewed_revision,
    expected_schema_sha256=trusted_schema_sha256,
    parent_checkpoint_sha256=previous_verified_archive_sha256)
restored = restore_checkpoint(
    downloaded_archive, fresh_restore,
    expected_archive_sha256=handoff_archive_sha256,
    ledger_identity=trusted_ledger_id,
    expected_schema_sha256=trusted_schema_sha256)
```

Default database bound is 8 MiB (maximum 32 MiB), manifest 16 KiB and elapsed
budget 5 seconds (maximum 10). Backup callbacks and SQLite progress handlers enforce
cooperative deadlines; synchronous filesystem/OS stalls are not a hard process
watchdog. POSIX directories/files use 0700/0600; on other platforms operators must
provide equivalent private ACLs. This is a cooperating-operator protocol, not
protection against hostile concurrent filesystem modification. A schema anchor
verifies structure, not scientific row semantics. Hashes and consistent backups
provide neither distributed locking nor operator authentication, freshness or
retention. Operators must verify the selected checkpoint's reference, ancestry,
revision and original runtime state before reconciliation. Existing Drive product
tools provide transport; this helper makes no upload/retention claim. End-to-end
per-job coordinator integration and separate capsule transport remain required.

## Local splitting for larger output archives

`weft.transfer_parts.split_file` and `reassemble` provide deterministic local
packing into ordered parts of at most 16 MiB (maximum 256 parts / 4 GiB). They
require an external full-file SHA-256; reassembly also requires the independently
recorded canonical-manifest hash. Fixed part names, exact file sets/order/sizes,
per-part hashes and the reconstructed whole-file hash are checked. No input is
extracted or executed. Destinations must be fresh; failures retain incomplete
files without a successful verification record. A returned local verification
never activates a job or asserts transport, retention or scientific acceptance.

The 16 MiB Drive probe establishes only the previously measured transport size.
Actual multipart cloud upload/download and reconstruction must still be qualified
on the declared job artifacts. Upload each part and manifest once, record exact
private locators and anchors, and verify every downloaded byte plus reconstructed
archive before normal ZIP/manifest validation. Unknown uploads hold the job;
never retry blindly. No Drive SDK, automatic uploader or approval bypass is added.
These helpers assume an operator-controlled filesystem; they do not defend against
hostile concurrent filesystem changes. POSIX staging is private (0700); Windows
operators must supply equivalent private ACLs. No compression or analysis method
is changed; split the completed archive as bytes.

Validation: eight focused local tests passed, including a 16 MiB-plus-seven-byte
boundary roundtrip, damaged parts, wrong external anchors, unexpected files,
traversal, changed source and bounds. This is local transport preparation, not
an end-to-end cloud multipart qualification.

## Qualified pilot transfer size

The first 16 MiB multipart trial failed during large-part readback, despite the
older independent 16 MiB probe succeeding. A separate 4 MiB+7 trial passed actual
cloud upload, authenticated download and reconstruction. Use the explicit
[operational amendment](../records/figure1-artifact-transfer-v2.json) for P001;
[trial evidence](../records/synthetic-multipart-20261011.json) preserves the failure.
The helper's generic 16 MiB bound remains unchanged. P001 uses 4 MiB parts and
at most 256 parts / 1 GiB. Every actual archive still needs its own readback checks.
The immutable job packet binds this amendment; scientific source, output format,
methods, container budget and network isolation are unchanged.
