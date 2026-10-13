# Current project state

Update this before stopping work, every session.

## PR #10 integrated; offline launch-intent recovery — 13 October 2026

The owner requested proceeding through the recommended steps. Root reviewed
PR #10's persistence, recovery, locking, stale-source and intake authority
boundaries at `d106463`, against unchanged main `5ca2a58`. No blocking defect was
found within its documented cooperative scope; this was not an independent human
or scientific review. The owner-authorized merge is
`5cd4178af7cd706a51b8fb814f94c223c2fa32ab`; main CI run **38335403318** passed.

The next scoped implementation adds an [offline launch-intent journal](docs/LAUNCH_INTENT_RECOVERY.md).
It binds occurrence/source/prompt/account/environment/policy, commits uncertainty
before a proposed provider call, rejects duplicate begins, preserves exact task
acknowledgements and holds conflicting/missing responses. Restored copies remain
inspectable but cannot mutate through this API. It calls no provider, supplies no
authenticated identity and does not replace distributed ownership or active-job
admission. The initial 12 targeted fixtures pass; two Windows test cleanup errors
were fixed by explicitly closing fixture-only SQLite connections.

The [readiness decision](docs/AUTOMATED_LAUNCH_READINESS.md) records the actual
external dependency: a permitted launcher exposing the intended environment and
account mapping. Browser denial remains unresolved; no alternate route was used
around it and no new worker was launched. Official documentation describes a
limited saved-VM recovery window, which is not durable archive storage or proof of
dot scratch retention. Choi, B4, existing ledgers and all activation flags remain
unchanged. B5 sample/reviewer/thresholds and M6 deployment decisions remain open.
The full suite passes **200 tests**, with the same 25 Windows ARM64 skips.
Offline documentation/configuration validation passes **179 links and 15 pins**;
Git whitespace checks pass. Automatic approval review blocked optional cleanup
of the two failed-fixture temporary directories; cleanup was not retried and
repository/source data were unaffected.
[Review and validation record](records/launcher-readiness-20261013.json).

## Synthetic launcher qualification — 13 October 2026

The owner authorized verifying the intended cloud route and one synthetic-only
task in existing `weft-pilot`. The [frozen qualification scope](docs/SYNTHETIC_LAUNCH_QUALIFICATION.md)
pins PR #10 revision `2c12090444e52108254f1c57831ecf80f239770f` and its 18 existing
handoff/intake fixtures, with one submission/attempt, a 180-second test-process
deadline and exact result readback. This is not approval to adopt the controls
on live screening catalogs, merge the PR or enable recurrence.

**One owner-operated cloud task is now observed.** The owner supplied the link to
`Run weft synthetic qualification`; supported task inspection and continuation work.
Root made no submission. Its configuration/version IDs match the recorded
`weft-pilot` publication, and a bounded readiness recheck changed the observed
enforcement state from unknown to current/enforced. Root did not verify that
environment or persist an intent before the owner's launch; the formal
pre-submission procedure is not claimed to have passed.

**Passed and idle:** the same task subsequently fetched and verified the exact
pin through the unchanged Git route, then ran all **18 tests once, with zero
failures/errors/skips, exit 0 and no timeout**. Existing unprivileged Bubblewrap
provided read-only source, private scratch and separate namespaces with no network
route. The 180-second subprocess deadline was armed; cancellation was not exercised.
The process exited and its launcher process group was absent. Root independently
reconstructed and hash-verified the 3,334-byte receipt and 98-byte log, then
confirmed identical same-task readback and idle task state. No synthetic job remains.
[Sanitized evidence](records/synthetic-cloud-task-20261013.json).

The first source fetch's authentication error remains unexplained. A read-only
Git discovery diagnostic returned HTTP 200 before the successful continuation;
no credentials, settings or access were changed. All earlier stop/diagnostic
receipts remain preserved and independently hash-verified. Private submission
state and exact receipts are under `runs/launcher-qualification-20261013`.

Browser automation remains blocked after the owner-confirmed allow setting and
restart/retry. Do not ask for that setting again, bypass the denial or create a
duplicate task. A manually launched task does not establish unattended launching,
PC-off invocation by Mir, cloud submission idempotency or retention. Choi closeout
is complete; B4 stays held and M6 disabled. No runtime code or scientific outputs
changed. This task's status does not establish quiescence of the interrupted B4 worker.

At this checkpoint, PR #10 control review was next; the later owner-requested
review/merge is recorded above. Remaining work: product troubleshooting for the
browser policy mismatch; supported automated-launcher,
ownership/retention and usage qualification before any recurrence. B5 still needs
an agreed independent sample, reviewer and frozen criteria. These are unresolved
roadmap gates, not jobs silently dispatched by this successful manual test.

Documentation/configuration validation passed: 168 local links and 15 source pins;
Git whitespace checks passed. No local fixture rerun was needed for this
documentation/evidence update; current PR CI is checked after publication.

## Backend continuation — 12 October 2026

Implemented the [cooperative screening handoff and private intake staging](docs/BACKEND_HANDOFF.md)
on a scoped branch from main `5ca2a58857b22968571c4389651862e17ee8dc35`.
Eighteen new synthetic tests pass; the full suite passes 188 tests (25 skips on
Windows ARM64), offline validation checks 161 links and all 15 pinned Ravel blobs
verify. Tests include interrupted-return recovery, no duplicate
claim, expiry holds, restored-copy refusal, current-source checks and intake
tampering/supersession. This is one-catalog software qualification, not a durable
distributed queue, authenticated worker or unattended deployment.

The [supported-launcher probe](docs/LAUNCHER_QUALIFICATION.md) found the documented
experimental cloud CLI. Its authenticated listing returned no tasks; the intended
environment/account route remains unverified. No cloud task was launched.
Direct messaging to the original Choi coordinator failed with `thread not found`.
The owner subsequently relayed Mir's successful continuity report: 30 events,
two scientific attempts and the held reservation, with the live database and
backup logically identical despite different SQLite byte hashes. A fresh
read-only check in the original worker at **23:01:33 KST on 12 October** verified
matching runtime identity, the original container exited with code 0/no OOM,
PID 0 and captured process identities absent in the visible namespace.
The owner approved the exact administrative checkpoint export, and Mir reported
one upload. Root independently verified the expected Drive identity, owner-only
file/parent, downloaded all 148,366 bytes and checked the archive/member hashes,
ZIP CRC, source/schema/parent anchors and a fresh inactive read-only restore.
Exactly one `administrative_closeout_reviewed` event is present: 31 total events,
the exact original 30-event prefix and both scientific rows preserved. That
checkpoint retains the historical HELD state. The owner then separately approved
release and the exact final-checkpoint export. Root independently downloaded the
156,558-byte final archive from the verified owner-only Drive destination and
passed hashes/CRC, identity/source/schema/parent and fresh read-only restoration.
All 32 events preserve the exact 31-event parent prefix and both scientific rows.
Exactly one `figure1_completed_reservation_released` event releases only the
completed Figure1 attempt. **Choi administrative closeout is complete, with its
final release remotely preserved and independently verified.** Scientific acceptance,
new-job authorization and automatic dispatch remain false; no restored copy was
activated. The frozen release event's pre-upload preservation status remains
historical; separate verification receipts establish current remote preservation
without another ledger mutation. Private evidence is under
`runs/backend-handoff-20261012`.

At this checkpoint, next steps were control review and environment verification
before requesting one synthetic-only launch. The owner subsequently authorized
that task on 13 October; see the current section above. No new job followed release.
Then qualify
PC-off operation and prepare [independent B5 evaluation](docs/B5_EVALUATION_PREPARATION.md).
B4 stays held, Choi never reruns, no further private export is authorized by this
change, and M6 recurrence remains disabled. [Evidence](records/backend-handoff-20261012.json).

At this historical checkpoint, [PR #10](https://github.com/xorca0711/weft/pull/10)
was open for explicit control review, not a draft. Both implementation CI runs
passed at `2fc69a8`; its later owner-authorized merge is recorded above.
The browser's saved `chatgpt.com` permission blocked the read-only environment
check; no workaround was attempted. The coordinator is **Mir** (its durable
record has no separate chat title). The cloud worker `Verify Weft network access`
is separate; it performed the fresh process check without touching Choi/B4 state.

## Backend stack integrated; bounded Choi M5 complete — 12 October 2026

Weft PRs **#4 -> #5 -> #6 -> #7 -> #8** merged in order, successors retargeted
to main, with main CI verified before each next merge. [Exact record](records/pr-stack-merged-20261012.json).
The owner approved the separate Choi output release, retained its bounded
descriptive discrepancy result and authorized Ravel #149 / Weft #9 integration.

Ravel #149 is merged at `34675134a5581989d028102a93ae51eebc84a501`; both main CI
workflows passed. All 15 outputs and original receipt are publicly recoverable,
hash-locked and restored in clean-checkout CI. No analysis reran, canonical RQ
was created, causal claim accepted or claim grade promoted. **M5 is complete for
this adapted, exposed descriptive benchmark.** [Closeout](docs/M5_PUBLICATION_PLAN.md)
and [authority/publication/merge record](records/choi-publication-20261012.json).

The initial frozen-ignore-file CI failure and exact-byte correction remain in
history. Local tests passed 158 cases (two skips); repository checks reached
11,169 after the human disposition document. That publication step left the
private reservation held. The subsequent owner-authorized administrative release
and independently verified final checkpoint are recorded above.

B4 stays held. Fresh-paper progress is 74 unique papers, 148 proposed RQ links,
five cloud link decisions, one held selected-text assessment, no completed fresh
candidate eligibility review or scientific dispatch. [Frontend/backend and storage map](docs/WORKFLOW_AND_STORAGE.md).

Next is B5 independent evaluation preparation and supported launcher/recovery
qualification. Freeze independent sampling, labels and criteria before a live
evaluation; already-exposed Choi/development papers do not qualify as unseen.
No new worker, scientific dispatch, policy update or recurring schedule is
authorized by this closeout. M6 remains disabled. Resolve B4 through the platform
before any permitted continuation. See [the marked roadmap](docs/IMPLEMENTATION_PLAN.md#established-state).

The owner also requested Choi's scientific trial dossier move to Ravel's
`weft_intake/choi-2020-p001/v1/`, with a root README trial note. The three
scientific documents are replaced here by navigation stubs; five public receipt
snapshots are copied unchanged for intake provenance. Runtime records and original
receipt ancestry stay in Weft. The transfer manifest records hashes; no source
data, private checkpoints or frozen outputs move. This documentation migration
is separate from fresh-paper eligibility and does not change Ravel's mission. Ravel
[#150](https://github.com/xorca0711/ravel/pull/150) merged the intake at
`7840089dc78a42c25679e2083541c5df1507cfc6`, after all four CI checks passed.

Weft #9 merged at `5ca2a58857b22968571c4389651862e17ee8dc35` with main CI passing.
Private preparation remains under
`runs/m5-publication-preparation-20261012`.

## Preserved B3 recovery / B4 platform hold — 12 October 2026

**Network enforcement and checkpoint restoration passed in the new worker.
B4 remains incomplete after a platform safety rejection.**
[Evidence and interruption record](docs/B3_CLOUD_B4_REVIEW.md) ·
[Check record](records/b3-cloud-b4-boundary-20261012.json).

The new worker's post-startup check reported current running/connected state,
restricted/enforced policy and matching desired/observed revision 4. Required
hosts and the Package managers preset are intact. The first two `unknown`
observations are retained as history. The environment name is owner-attested
and corroborated by its historical setup receipt, not a current API display name.
No configuration edit or restart was needed for the successful recheck.

Setup remains d031cef. A separate clean PR #7 checkout at d95d558 restored the
exact 522,632-byte archive: SHA-256, CRC, safe paths, all 42 manifest members,
catalog hash, SQLite integrity, foreign keys and expected counts passed.
All 55 targeted tests, 119 documentation links and 15 Ravel source pins passed.
The review store issued the same B3 packet without network access; no new data-use
or RQ assessment was submitted in the observed execution.

Official acquisition documentation was retrieved. A source-archive request then
started, with HTTP 200 and at least 65,536 bytes retained at the last ledger read.
The turn failed with a platform safety error citing potential dual-use biology.
The error does not identify the triggering content or establish that the paper
itself is unsuitable. An administrative preservation-only follow-up was also
rejected before any tools ran. No alternative route or retry was attempted.

Last observed B4 usage: **6 of 12 distinct requests**, one attempt each, and
**1,004,901 counted bytes**, including historical requests. These are an
in-progress snapshot, not final reconciled totals. Source-download completion,
final file hashes, database counts and post-interruption process/store quiescence
remain unverified. No figure/supplement pixel review, complete coverage record,
new checkpoint export or scientific acceptance is established.

Next: platform review of the rejected task is required before any permitted
continuation. Do not bypass filtering by another worker, tool, context or renamed
request. First reconcile process state, partial/complete bytes, request budget
and the review store without overwriting original receipts; then determine which
work can proceed. The old worker and Choi remain preserved; Ravel is unchanged.
No new access, deployment, analysis, schedule, export or merge is authorized by
this status update. Private locators and the exact error are retained under
`runs/b3-cloud-b4-review-20261012`.

## Historical B3 implementation checkpoint — 12 October 2026

[PR #7](https://github.com/xorca0711/weft/pull/7) implements this slice. B3 now
issues a source-bound evidence packet, inventories cached JATS figures and
supplements, copies bounded explicitly supplied local artifacts, and records
separate data-use and RQ-compatibility proposals. Commands, record semantics and
the backend diagram are in [the B3 guide](docs/EVIDENCE_QUALIFICATION.md).
New consistency checks are proposed for explicit PR review; G3–G8 authority,
policy activation and Ravel scientific admission are unchanged.

The [cached-source development test](records/evidence-qualification-20261012.json)
found six figure entries and two supplement entries in the existing reviewed
candidate's XML. No new pixels, supplements or dataset files were inspected.
Both proposals remain held. An inactive copy preserved the original checkpoint,
source bytes, five screening decisions and 20-event prefix; two B3 events were
added only to that development copy. Fresh-path recovery was idempotent, with
zero network calls or duplicate events. This exposed test does not qualify B3
cloud deployment or scientific screening accuracy.

The full Windows suite passed 168 tests with 24 platform skips; the expanded B3
suite then passed 16 tests with one host symlink skip. Linux CI passed all 170
tests without skips on code revision `11affb4`; both push and PR checks passed. No biological analysis or discovery reran. Choi and the active scientific
ledger remain separate and unchanged. Local private copies are under ignored
`runs/evidence-qualification-20261012-v1`, closed and inactive.

Next: review this new software slice stacked on #6 (preceded by #4 and #5), and
qualify its pinned revision in the existing screening cloud route. Then perform
a bounded B4 review with actual figure/supplement coverage, data lineage and
RQ-fit proposals. A new source host, credential, unsupported artifact adapter or
deployment choice must be resolved before that dependent action. Existing access
has not been expanded. B5 independent unseen-paper evaluation precedes any
recurrence proposal. Choi publication is still an open parallel track.

## Prior completed screening qualification — 12 October 2026

[PR #6](https://github.com/xorca0711/weft/pull/6) implements portable reading paths
and verified Windows/POSIX legacy-address reconciliation. Linux CI passed all
**154 tests without skips** at code pin `1945515`. The original local checkpoint
passed two-root recovery with unchanged evidence and decisions. The PR is stacked
on #5; refresh/retarget after predecessor merges. Nothing was merged here.

The approved Europe PMC host amendment and separate screening-only `weft-pilot`
task are live. Setup/startup `d031cef`, existing hosts and the original Choi worker
were preserved. Actual proxy/TLS connectivity, clean isolated `1945515` source,
73 targeted cloud tests, 111 links and 15 pinned Ravel blobs passed. Initial
network failures were command-sandbox denials, resolved through normal reviewed
permissions; no proxy bypass or platform outage was established.

Three cloud searches returned **82 observations / 74 papers / 148 RQ links**.
The five-link screening pass proposed **one read next, one hold and three link
rejections**; 143 links remain deferred. One OA XML yielded four selected-text
statements and a held next action. Figures, supplements, datasets, eligibility
and scientific acceptance remain unassessed. The window/profile was already
observed locally; this is operational qualification, not independent accuracy
evaluation. [Evidence](records/screening-portability-20261012.json) and
[qualification guide](docs/SCREENING_CLOUD_QUALIFICATION.md).

The **before** checkpoint passed owner-approved Drive export and independent root
download, CRC, all 20 members, read-only SQLite and pending-packet verification. After
screening, worker-local fresh-path recovery passed cached search/XML replay with
zero network calls, idempotent responses, unchanged caps/evidence and the original
eight-event prefix. Final counts are 20 batch events and five review events.
All cloud stores are quiesced with no active writer.

The **after** checkpoint also passed exact owner-approved upload and worker
readback: 522,632 bytes, SHA-256
`7edfa55a6349b2bd2ace5db26a24ab0fec9a0609e6345b6119be5c6e5476fb8f`.
Root independently downloaded and verified all 42 manifest members, SQLite
integrity/foreign keys/counts, the original eight-event prefix, 17 unchanged
source files and all packet/response/XML bindings. A separate Windows restore
replayed completed searches, five responses and the saved XML assessment with
zero network calls, unchanged database rows and no duplicate events. All cached
paths resolved inside the restored store. Both restores remain inactive.

Manual cloud handoff and checkpoint recovery are qualified within these bounds.
Private Drive IDs, worker paths and receipts stay in ignored
`runs/screening-cloud-qualification-20261012`. The first Windows replay was stopped
by sandbox path-access denial; the normal permission retry passed on a fresh copy.
No checkpoint or evidence was repaired to make the check pass.

Next: review the stacked #4 -> #5 -> #6 software PRs and refresh each integration
base before merging; implement B3 figure/supplement coverage, dataset lineage and
RQ-compatibility records; then freeze an unseen-paper evaluation. A future
unattended launcher or recurrence needs its own supported deployment and scope
decision. No additional access decision remains for this completed qualification.

This remains a manually launched cloud-agent interface, without an unattended
model service or schedule. Choi's ledger/reservation, analysis and publication
track are unchanged. No Ravel acceptance, canonical RQ, scientific rerun or merge.

## Historical backend implementation checkpoint — 12 October 2026

B1 bounded coordination and B2 screening packet/response mechanics are implemented
on a scoped branch. [Guide](docs/BATCH_SCREENING.md) and
[live development record](docs/BATCH_PILOT_20261012.md) own commands and limitations.
Three Europe PMC streams returned 82 occurrences / 74 papers / 148 A0/A1 links.
Five links across three papers were screened: one read next, two holds, two link
rejections; 143 links remain deferred. One XML packet and four selected-text
statements were checked; the assessment stays held for further source review.
No figure/supplement/data eligibility, RQ support or human acceptance is claimed.

The completed searches replayed without network calls; all five response replays
were idempotent. A private 34-file checkpoint passed every hash and fresh read-only
SQLite integrity/count checks. It was not activated. This is a local development
test using the current agent, not cloud deployment qualification. Tests found and
fixed malformed-observation handling and excessive CLI output. Final review added
an overlapping-batch guard preserving existing decisions; focused tests pass.
The prior full Windows run passed 140 tests with 23 platform-specific skips;
four additional focused tests subsequently passed (22 new tests total). Both Linux CI runs passed on code revision `5915ba7`: **144 tests, no skips**,
plus documentation validation (105 links / 15 pins).
[PR #5](https://github.com/xorca0711/weft/pull/5) is stacked on PR #4; merge #4
first, then retarget #5 to main and refresh checks. Neither PR was merged here.

Next: review/merge this software change through its PR; qualify cloud handoff and
restoration, including cached XML path reconciliation; implement B3 coverage and
dataset records; review query disambiguation and paper-level ordering; then freeze
an independent screening evaluation. No new credentials, schedule, paid model API,
environment update or cloud launch occurred. The existing Choi ledger, reservation,
Ravel PR #149 and publication hold remain unchanged. Choi M5 stays separate.

## Historical planning checkpoint — discovery and screening backend — 12 October 2026

At the owner's request to prioritize backend automation, the roadmap now separates
Choi's pending publication from [discovery/screening implementation](docs/DISCOVERY_SCREENING_BACKEND.md).
Current code provides manual Europe PMC search/dedup, pinned RQ context, the
candidate buffer, XML reading packets and mechanical provenance checks. It does
not run an autonomous semantic screening/gating loop. All 32 RQ identities can be
loaded, but initial search profiles cover A0/A1 only.

Next: implement and fixture-test B1 batch coordination, B2 structured cloud-agent
handoff and B3 separate reading/data/RQ decisions; then run a bounded fresh-paper
screening batch. Qualification and recurrence follow after review. No new Choi
analysis, scientific acceptance, schedule, credential or backend deployment was
performed in this planning update. Choi M5 remains open and its held reservation
must be reconciled before new live dispatch. Documentation validation passed: 93 local links, 15 unchanged Ravel pins and
scientific execution disabled. Diff-whitespace checks passed.

## Historical checkpoint — Choi scientific review complete; publication pending — 12 October 2026

[Scientific review](docs/PILOT_CHOI_SCIENTIFIC_REVIEW.md) and its
[record](records/choi-scientific-review-20261012.json) hand off findings to Ravel.
All 15 outputs reconcile with the saved H5AD across 1,497 assertions; all five
figures were inspected and compared with the audited paper. No analysis reran.
The four-state adaptation lacks pAT2; day-28 exclusions (28.06%) and 520/917 DATP
cells retained despite hAT2 subcluster labels constrain interpretation. Coarse
patterns agree, but exact five-state and mechanistic reproduction are unsupported.
No new RQ, claim promotion or human acceptance is recorded.

M4b review is complete for this attempt; M5 publication/integration remains open.
Next: choose and qualify durable availability of all outputs, including the
385,675,968-byte H5AD, under Ravel's unchanged validator. PR #149 stays draft; no
partial receipt is registered. The coordinator remains at its last verified
30-event checkpoint and held reservation; this local review did not mutate the
ledger. Reconcile and checkpoint before any later job. No new dispatch, schedule,
paid service or data export. Offline validation passed: 89 local links, 15 unchanged Ravel pins and scientific
execution disabled. Diff-whitespace checks passed.

## Historical checkpoint — Figure1 export verified; scientific review pending — 12 October 2026

The same cloud worker recovered and completed the original approved export without
rerunning analysis. All **26 parts plus the transfer manifest** are in the original
owner-only Drive folder. Worker and independent root downloads/reconstruction
matched **105,848,914 bytes**, archive SHA-256 `e1f8ee36…`, transfer-manifest SHA-256
`f73b416c…`, ZIP CRC and **all 99 manifest entries** (100 ZIP members including the
manifest). The original run-receipt hash is unchanged. Root separately verified
all 27 remote file sizes, parent and owner-only permissions.

The final checkpoint also passed independent byte/schema/integrity and fresh
read-only restore checks: **30 events**, the same two scientific rows, and exact
27→28→29→30 event prefixes. Its SHA-256 is `c8ac521d…`; the intermediate streaming
proxy failure and worker-verification checkpoints are preserved. No copy was
activated by root. [Exact execution and verification record](records/choi-figure1-execution-20261012.json).

The optional direct-streaming probe received HTTP 403 from the worker proxy. The
existing approved Drive connector route completed with standard-input byte
materialization. No network allowlist expansion, account switch, duplicate upload,
source modification or scientific rerun occurred. Private locators stay ignored.

**Remaining work:** review the original receipt and QC/denominator/marker tables,
inspect figures, write the bounded discrepancy and candidate/no-candidate report,
and resolve publication of every declared output under Ravel's unchanged validator.
The 385,675,968-byte H5AD still needs a reviewed durable publication route. Archive
integrity does not establish scientific validity. No acceptance, new RQ, numerical
dispatch or reservation release follows from this transfer verification.

PR #3 was merged by the owner into main, bringing the README backend diagram and
previously merged PR #2 controls into the integration base. This continuation is
documentation/evidence bookkeeping on a scoped branch; frozen job pins remain.

## Historical partial-export checkpoint — 12 October 2026

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

## Historical execution and initial export hold — 12 October 2026

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
