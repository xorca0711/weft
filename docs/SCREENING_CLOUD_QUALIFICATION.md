# Screening portability and cloud qualification

**12 October 2026: bounded manual cloud screening, both Drive checkpoints and
independent Linux-to-Windows cached recovery passed.** The host
amendment and one separate screening-only task were approved. The original Choi
worker, scientific state and artifacts are preserved.

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
skips, including the symlink test that requires host support. Linux CI passed all 154 tests without skips on code revision `1945515` in
[PR #6](https://github.com/xorca0711/weft/pull/6). The record distinguishes this local test from actual
cloud handoff and recovery, completed below as a separate observed test.

## Historical original-worker readiness

The current worker reported Python 3.12.14, Git 2.52.0, writable parent space for
a separate screening directory, and approximately 9.75 GiB free disk. Its restricted
network snapshot permits GitHub, raw GitHub and codeload, but not Europe PMC's
`www.ebi.ac.uk` API host. It verified the existing Drive account and owner-only
artifact folder without changing them. No credentials are included in public
records. The managed-runtime skill/tool was unavailable in that worker turn, so
the environment's current identity and readiness are not independently confirmed.
Do not equate executor responsiveness with managed-environment qualification.

## Approved and published network amendment

The owner approved adding only `www.ebi.ac.uk`. The root opened the existing
`weft-pilot` through Settings > Codex Cloud > Edit, verified repository
`xorca0711/weft`, Only me visibility, the package-manager preset, and unchanged
setup/startup pin `d031cef`. The extra-host list changed from
`ftp.ncbi.nlm.nih.gov` to that same host plus `www.ebi.ac.uk`. The UI showed one
network change, then confirmed Published / Environment has been published.
Secrets, environment variables, scripts and visibility were not changed. The adapter
uses HTTPS GET for bounded metadata searches and available open-access XML at
`https://www.ebi.ac.uk/europepmc/webservices/rest/`.

The subsequent same-worker check at 18:08:51 KST still found a restricted policy
without `www.ebi.ac.uk`, with the NCBI host retained. Its policy SHA-256 is in the
linked evidence record. The bibliographic GET was not attempted. The current
worker still lacks a managed environment/config-version capability, and the
inspected chat controls expose no in-place update action. Publication is verified;
propagation to this existing worker is not. Do not edit its policy snapshot or
reset a runtime that holds Choi evidence.

**Approved deployment:** the owner approved one screening-only cloud task using
the updated existing `weft-pilot`. It was created with the original Choi worker
preserved. Its managed status progressed from provisioning to running/connected,
with current observations and an enforced policy containing all four required
GitHub/Europe PMC hosts. Its original d031cef checkout remains clean, and Drive
identity and owner-only destination were confirmed.

The first GET and socket diagnostic failed in the default restricted command
sandbox. With normal reviewed execution permission, the same inherited proxy/TLS
GET returned HTTP 200 at 18:18:28 KST (1,117 bytes; valid JSON, one record).
This does not establish a sidecar outage. No proxy, CA, TLS or route was changed.
The separate source is clean at `1945515`; 73 targeted tests, documentation
validation and 15 Ravel blobs at `bfe26b8` passed without installing dependencies.

## Cloud batch and resolved before-export hold

The batch freezes profile `alveolar-transitions`, FIRST_IDATE 12 September through
12 October 2026, all three profile streams, and caps of 12 search attempts,
100 records/search, five screening links and one XML read. The same profile/window
was already observed in local development; this is exposed operational
qualification. Fresh cloud searches at 18:23:32–18:23:37 KST returned 82 observations,
74 papers and 148 links. The first packet was issued for `doi:10.1002/adhm.71751`.
The subsequent bounded screening results are recorded below; no scientific
execution has occurred.

`cloud-batch-20261012-v1-before-screening.zip`: 389,137 bytes; SHA-256
`b4dff3298207cfb800d19d74a9f03dc79f3b86ecba853d9e9f9ac27706814b32`.
Its 20 manifest members plus manifest passed the worker's fresh inactive local
restore: CRC, safe unique regular paths, all sizes/hashes, SQLite integrity,
foreign keys/counts and pending-packet binding. Source/store hashes were preserved.
The archive contains public metadata/abstracts, queries and RQ context plus
private execution paths, workflow identifiers and timestamps. No full-text XML,
credentials/environment dumps or Choi state were included; a bounded JSON
secret-pattern scan found no matches, not an exhaustive privacy guarantee.

Automatic approval review rejected a combined preparation/upload instruction
while its future payload was unknown. The worker then prepared the archive
locally. The owner directly approved that exact archive in the worker; upload
and readback passed with sharing unchanged. Root independently downloaded it,
verified all 20 members, SQLite integrity/counts and pending-packet binding,
and retained an inactive read-only restore before releasing screening.

## Screening result and after-checkpoint

| Paper / RQ | Agent reading-priority proposal | Inspected-scope reason |
|---|---|---|
| `10.1002/adhm.71751` / A0 | Hold | Repair context; conserved transition-programme comparison unclear |
| Same paper / A1 | Reject link | No transitional-state regulatory discriminator or linked maturation endpoint described |
| `10.1002/adma.75042` / A0 and A1 | Reject both links | Periodontal alveolar bone query mismatch |
| `10.1002/advs.77773` / A0 | Read next | Adult AT2/progenitor/differentiated comparisons warrant source review |

Five links were assessed and 143 deferred. One XML attempt succeeded for
PMC13634473; four source-bound selected-text statements retain `next_action: hold`.
Figures, supplements, datasets, eligibility and acceptance are unassessed.
Local development had two holds and two rejections; this cloud pass had one
hold and three rejections. Different runs/agent contexts do not constitute a
controlled accuracy comparison. No independent quality metric is claimed.

Worker-local recovery preserved the original eight-event prefix, evidence and
caps. All five response replays returned `already_recorded`; completed searches
and cached XML used a fetch callback that fails on network access and made zero
requests. No changed rows or duplicate events were reported. Final database:
20 batch events, five review events. All stores are now quiesced/inactive.

After archive: `cloud-batch-20261012-v1-after-screening.zip`, **522,632 bytes**,
SHA-256 `7edfa55a6349b2bd2ace5db26a24ab0fec9a0609e6345b6119be5c6e5476fb8f`;
42 manifest members plus manifest. It contains public abstracts, queries/RQ context,
one OA CC-BY XML/derived text and private execution paths, identifiers/timestamps
and screening responses. The bounded secret-pattern scan found no matches;
unrelated/Choi state and environment dumps are excluded.

The owner approved the exact after archive directly in the worker. Upload and
readback passed with owner-only sharing unchanged. Root independently downloaded
it and verified ZIP CRC, all 42 member hashes, SQLite integrity/foreign keys/counts,
the original eight-event prefix, 17 unchanged source files, saved response
identities/citations and XML bindings. A separate Windows verification copy
replayed completed searches, all five responses and the XML assessment with zero
network calls and unchanged database rows. Cached paths resolved inside that copy;
all assessment replays returned `already_recorded`. The first root replay was
blocked by Windows sandbox path access; a normal permission retry passed on a
fresh copy without modifying code or evidence. Source and verification stores
remain inactive, with no competing writer. Private locators and detailed receipts
are retained outside version control; public receipt hashes are in the record.
This qualifies an operator-launched pull interface only, not autonomous launches,
scheduled operation, scientific eligibility or model screening accuracy.

## Qualification closeout and next boundary

The approved host update, separate screening task, exact source checks, bounded
discovery, source-bound response capture, before/after Drive readback and fresh
cross-host recovery are complete. No additional access decision remains for this
qualification. All Choi state and the setup/startup source pin were preserved.

Next implement B3 figure/supplement inspection coverage, dataset lineage and
RQ-compatibility records. Freeze a separate unseen-paper evaluation before
reporting screening accuracy. Unattended agent launch, recurrence, usage limits
and recovery authority remain deployment decisions for a later slice. Private
Drive backups provide verified recovery points, not a distributed writer lock
or a guarantee that a cloud workspace survives a restart.
