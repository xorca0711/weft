# Screening portability and cloud qualification

**12 October 2026: path portability passed local checks; cloud handoff/recovery is held.**
The owner requested use of the existing cloud environment and a stop before new
access or deployment decisions. The existing worker is responsive, but its
current network snapshot excludes `www.ebi.ac.uk`. No environment setting,
network policy, scientific state, Drive artifact or Choi reservation was changed.

[Portability evidence](../records/screening-portability-20261012.json) ·
[Batch commands](BATCH_SCREENING.md) · [Current state](../PROGRESS.md)

## Implemented path repair

New batch reading results persist `directory` as one generated store-relative
directory and `directory_scope: discovery-store-relative-v1`. `batch-read` adds
`resolved_directory` only when presenting the result. Consumers should use that
field for local file access; never persist it as the portable address.
The standalone `prepare-reading` command keeps its earlier output contract.

An old absolute path still works within its original store. A moved legacy store
requires an explicit addressing amendment, rather than silently stripping the
path prefix. Quiesce the original writer and use a designated restored copy:

```bash
python -m weft batch-relocate-reading --store /workspace/screening-qualification/restored \
  --batch BATCH_ID --source-root 'X:\GitHub\weft\runs\backend-pilot-20261012-v1'
```

The command interprets Windows or POSIX syntax independently of the current OS.
Every old path must be exactly one generated reading directory beneath the
provided root. Each mapping must match its saved receipt, screening identity,
packet hash and source hash. Unknown scopes, traversal, foreign roots, linked
evidence and tampering fail. All mappings are checked before one transaction
updates addressing and appends private history containing the original result.
Source files, source contracts, statements, reviews and caps are not rewritten.
Repeated reconciliation is idempotent. This does not implement distributed
writer fencing; the operator must prevent competing writers.

## Observed recovery test

The original private 34-file checkpoint of the 74-paper development batch was
verified and restored into a new local directory. One legacy reading address was
amended. All 33 non-database files retained their original hashes; the database
added only one path-amendment event. Counts remained three searches, 148 candidate
links and five reading-priority events. A second copy under a different root
resolved the same cached XML and returned `already_recorded` for its assessment.
The original archive remained byte-identical. No retrieval or analysis reran.

Tests cover Windows/POSIX legacy addresses, cross-root cache reuse, source/packet
binding, path rejection, linked files, unchanged decisions and caps, and repeated
amendments. The Windows full suite passed 154 tests with 24 platform-specific
skips, including the symlink test that requires host support. Linux CI is the
remaining platform check. The record distinguishes this local test from actual
cloud handoff and recovery; the latter has not run.

## Existing worker readiness

The current worker reported Python 3.12.14, Git 2.52.0, writable parent space for
a separate screening directory, and approximately 9.75 GiB free disk. Its restricted
network snapshot permits GitHub, raw GitHub and codeload, but not Europe PMC's
`www.ebi.ac.uk` API host. It verified the existing Drive account and owner-only
artifact folder without changing them. No credentials are included in public
records. The managed-runtime skill/tool was unavailable in that worker turn, so
the environment's current identity and readiness are not independently confirmed.
Do not equate executor responsiveness with managed-environment qualification.

## Concrete access change awaiting the owner

Add only `www.ebi.ac.uk` to the existing `weft-pilot` allowed hosts and publish that
network revision after verifying the selected environment's identity and current
configuration. Retain all existing hosts, secrets, sharing and setup source pin
`d031cef`; do not switch services, add an API key or enable a schedule. The adapter
uses HTTPS GET for bounded metadata searches and available open-access XML at
`https://www.ebi.ac.uk/europepmc/webservices/rest/`.

This is a new external-host grant. It is not covered by the earlier approval for
the single NCBI FTP host. If current supported UI/runtime inspection cannot
establish the intended environment, stop before applying the change and resolve
that access or dependency separately. A published setting alone is not proof that
the existing worker has received it; verify the actual worker policy afterwards.

## Qualification sequence after that decision

1. Verify the existing environment and runtime observations through supported
   tools/UI. Apply only the approved host amendment and inspect the resulting
   worker policy before requests. Stop on a missing tool/identity/host instead of
   introducing a paid API, alternate proxy or another environment.
2. Fetch the reviewed portability revision into an isolated screening workspace.
   Run offline checks and verify the Ravel source pin. Keep every Choi path,
   scientific ledger, reservation and artifact untouched.
3. Designate one screening coordinator. Preserve and verify a private before-job
   checkpoint and immutable packet using the existing owner-only Drive route;
   respect any payload-specific approval review. This is separate from the Choi
   scientific ledger and does not claim a distributed lock or retention guarantee.
4. Have the existing cloud agent consume one source-bound screening packet and
   return a structured proposal within its declared scope. Freeze query/window,
   input identity, code revision and limits first. Preserve prior exposure and do
   not claim independent/blinded evaluation. No scientific execution is allowed.
5. Preserve the response and after-job checkpoint. Quiesce that writer, restore
   to a fresh directory, verify all hashes/SQLite integrity, reconcile legacy
   addresses if necessary, and prove cached packet reuse and idempotent ingestion
   without refetching, rereading through a second agent, or rerunning analysis.
6. Independently read back the private checkpoint and compact qualification report.
   Record actual success, failure or interruption and the exact remaining hold.
   Do not call handoff/recovery qualified before both state and returned output
   have been recovered. Recurrence and scientific eligibility remain separate.
