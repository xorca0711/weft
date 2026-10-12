# Development and decisions

## AI assistance

OpenAI Codex prepared the initial documentation, configuration, source-pin
manifest, offline validation code and tests. The owner requested the project
and public creation. The initial scaffold executed no biological analysis. Later
manual cloud execution and review are recorded in the dated entries and PROGRESS;
autonomous workflow completion and scientific acceptance are not claimed.

## Responsibility record

| Date | Item | Proposed by | Decided by | Decision | Reason |
|---|---|---|---|---|---|
| 2026-10-11 | Separate repository with implementation plan and README diagram | Owner | Owner | Requested | Develop the literature-to-reanalysis workflow alongside Ravel |
| 2026-10-11 | Public visibility | Codex offered options | Owner | Public from the start | Explicit response in the creation task |
| 2026-10-11 | Weft name, architecture and Choi benchmark | Codex | Pending owner review of details | Implemented as initial proposal | Natural relationship to Ravel; known successes and limitations make an auditable pilot |
| 2026-10-11 | Complete Choi figure/supplement/data review and recommend a worker before analysis | Owner | Owner requested scope; scientific acceptance remains unissued | Review implemented on existing PR; worker recommendation awaits selection | Preserve the reading/execution boundary and qualify actual input shape |
| 2026-10-11 | Dot coordination and Codex Cloud execution; cloud-first roadmap | Owner selected architecture after Codex proposal | Owner for architecture; scientific acceptance pending | Update plan and request access/dependencies; no extra local PC | Cloud execution addresses hardware constraints; no paid fallback or schedule authorized |
| 2026-10-12 | Prioritize discovery/screening backend before Choi publication closeout | Owner raised priority; Codex structured slices | Owner requested reconsideration; detailed implementation remains reviewable | Document next backend slices; no runtime activation | Already-read Choi is useful for recovery/regression, not sufficient to evaluate candidate selection |

| 2026-10-12 | Implement batch coordinator, screening interface and fresh-candidate test | Owner requested scope; Codex implemented | Owner authorized work; code/scientific acceptance pending review | Scoped software change and local development test; no deployment | Exercise search-to-screening independently of Choi publication |

| 2026-10-12 | Portable reading references and existing-cloud screening qualification | Owner requested scope; Codex implemented path fix | Owner authorized work; new network grant pending | Local recovery passed; cloud work stopped at missing host permission | Preserve evidence and Choi while requiring explicit access decisions |

## Rejected or substantially revised AI proposals

| Date | Proposal | Why changed | Changed/rejected by |
|---|---|---|---|
| 2026-10-11 | Private initial repository | Owner explicitly chose public; personal configuration remains excluded | Owner |
| 2026-10-11 | Blanket 16 GiB local worker allowance | Audited Windows host has about 15.6 GiB total memory; recommend separate 32 GiB Linux host or a qualified 6 GiB Windows fallback | Codex revision; host selection pending owner decision |
| 2026-10-11 | Treat the Choi pilot as exact reproduction before qualifying methods | Published Louvain/manual exclusions and Ravel Leiden/MAD/annotation rules differ; exact author-cell set is unresolved | Codex revised proposal to explicitly adapted descriptive reanalysis |
| 2026-10-11 | Separate Linux worker as the default next decision, preferably 32 GiB RAM | Owner cannot add a PC and selected dot/Codex Cloud; 32 GiB was unmeasured conservative sizing. Qualify cloud first | Owner selected direction; Codex revised deployment stages |
| 2026-10-12 | Serial roadmap implying Choi integration must precede fresh-candidate screening qualification | Candidate screening can be implemented and evaluated independently; preserve Choi publication as an open parallel track | Owner feedback; Codex revised plan |

| 2026-10-12 | Treat the first lexical candidates as a priority shortlist or completed scientific screening | Dental alveolar matches, duplicate per-RQ review cost and incomplete source coverage require separate evaluation; retain frozen results | Codex implementation review; proposed query/ranking revisions remain unadopted |

Future reviews append decisions and rejections rather than overwriting them.
Repository creation does not mean every scientific or operational proposal has
been accepted. No software license has yet been selected by the owner; public
visibility alone does not grant an open-source license.

## Discovery and buffer implementation — 11 October 2026

The owner requested milestone execution and assessment of direct RQ coupling.
Codex implemented bounded retrieval, conservative bibliographic identities,
persistent receipts/cutoffs, pinned RQ context and a review buffer. The owner then
selected local Codex with manual runs for the reading stage. This authorizes that
implementation choice, not scientific claim acceptance or a compute budget.

The revised design places a proposal buffer between query matching and Ravel
evidence. Changed sources/context require renewed reading review. Different
publication editions remain separate until reconciled; no study count is inferred.
The original unrestricted recent query was retained as a truncated attempt and
replaced by a title/abstract profile after observing acronym-related noise.

Scientific gate semantics and buffer boundaries are explicit review items in the
implementation PR. No Ravel governance check was weakened or biological rerun
performed. Automated tests and source locators validate software properties only.

## Choi source and input review — 11 October 2026

Codex inspected all main figures and S1-S7, reconciled the official supplement
with the institutional edition, mapped three GEO accessions and checked the local
GSE145031 archive. No scientific pipeline was executed. The original XML reading
record remains immutable; a new review record extends its coverage. Download
failures and the corrected cover-page alignment remain in local receipts.

The README's implementation descriptions now use the document convention's
"Descriptive only" status; this is a vocabulary correction, not scientific
validation. The roadmap separates the completed manual review from M2 evaluation,
M3 runtime enforcement and M4 numerical work. Ravel's completed directory migration
is reflected in the handoff. Governance, validators and activation flags are unchanged.

## Cloud execution roadmap — 11 October 2026

The owner selected dots/Codex Cloud and confirmed Create environment and the Weft
repository selector are available. Codex updated the implementation stages,
README workflow, environment requirements, pilot metadata and cloud setup handoff.
The change supersedes unmeasured hardware sizing without altering gate semantics.
No environment, dot task, scientific run or schedule was launched. All existing
source receipts remain immutable. Runtime qualification, product-usage budgeting
and durable ledger/artifact handling remain implementation work.

## Cloud setup and synthetic ledger — 11 October 2026

The owner explicitly requested UI environment setup at d031cef, publication after
successful checks, and continuation toward Choi. Browser account access is pending
resolution. Codex implemented a bounded synthetic-only M3 foundation while waiting;
no execution gate was weakened or scientific authority invented. The new ledger
records cooperative transitions and cannot establish real process termination.

## Published setup and independent restore — 11 October 2026

Account access was resolved. Codex configured private weft-pilot in the UI using
the exact authorized d031cef baseline, reviewed 58 cloud tests and 15 pinned Ravel
blobs, and published after setup and independent synthetic restore checks passed.
The archive was transferred via rendered base64 after the file-viewer download
was unconfirmed; its checksums/CRC were verified on a separate Windows host.
This is narrow setup evidence, not a durable cloud artifact service. Initial
receipts remain unchanged; the new public record distinguishes those observations
from outstanding M3/M4 controls. No scientific gate, source contract, Ravel file,
activation flag or scientific result was changed. No merge is claimed.

Fresh-task qualification independently matched the published configuration version
suffix and passed Docker memory/PID/network/non-root/read-only/cancellation checks.
The owner selected private Google Drive. A new owner-only folder and authenticated
48,400-byte same-task roundtrip passed; a separate cloud restore is being verified.
Private Drive locators remain ignored. Startup skill discovery and managed-network
status differ from setup; receipts retain those limitations rather than claiming
complete M3 readiness. The exact d031cef environment baseline remains unchanged.

Independent cloud-to-Drive-to-fresh-cloud restoration then passed SHA-256, 32
member CRC/path checks and all 12 included source/command hashes. No PC/source-task
files or archived code were used. One referenced setup-script digest cannot be
checked because that file is absent from the ZIP; this limit remains explicit.
This qualifies the demonstrated synthetic recovery path, not retention guarantees,
large scientific artifacts or a shared authoritative ledger.


## Trusted synthetic executor — 11 October 2026

The owner authorized code/tests/docs on PR #2 from exact 1866f96, superseding the
qualification task's read-only source restriction. Codex implemented a fixed-fixture
Docker adapter and strict content-addressed receipts/restoration. Published d031cef
setup and frozen qualification artifacts remain unchanged. Hashes establish content
integrity under a trusted adapter/coordinator; they do not establish actor authority
or scientific success. Executor-bound attempts cannot use legacy self-report release.

The local success/failure/cancellation/unknown distinction is implemented and tested;
whole-job completion, coordinator authority, Drive transport integration and product
dispatch remain unimplemented. Actual bounded success/cancellation used the qualified
cached image without repeating the broad capability probes. 94 tests and offline
validation passed. Public files contain no Drive folder/owner details or raw logs.
No scientific gate, activation flag, Ravel source or environment configuration changed.

## Prelaunch recovery correction — 11 October 2026

Root review identified that preserving only a lease-token hash and code fingerprint
could leave an interrupted attempt unrecoverable. The owner authorized a correction
from exact 4a2bc7a on PR #2. New attempts now save an exclusive, restricted private
claim/source capsule before Docker operations, authenticate it against the same
ledger and load the exact saved package after restart. The capsule is ignored and
excluded from public receipts, ordinary output archives and logs. No original
missing materials are fabricated. The historical intermediate attempt stays held.

102 tests cover persistence failure before Docker, secret exclusion, restrictive
permissions, missing/tampered material and separate-process restoration using the
saved claim/source identity. One bounded actual launcher-interruption/restarted-
process recovery passed against the already pinned image, including terminal
process checks, cleanup and archive verification. Scientific coordinator storage
still awaits owner choice; neither task-local persistence nor this recovery test
establishes remote authority or dot persistence. Policy flags remain false.

## 11 October 2026 — checkpointed manual deployment choice

The owner selected one coordinator with private Drive backups before/after each
job and explicit recovery after interruption, instead of a new persistent service.
A dot delegated one read-only cloud check and retrieved its expected scientific
hold; the same dot verified local SQLite execution and an authenticated private
checkpoint/restore. records/manual-coordinator-20261011.json preserves coverage.
No retention, distributed lock, scientific authority or unattended activation is
inferred. The numerical stack is being qualified with synthetic data only. A new
clean Ravel worktree on X: was prepared at bfe26b8; no Ravel source/data was edited.

Root review found POSIX-only recovery fixtures were not platform-scoped. Windows
now skips those cases explicitly; portable artifact tests remain active. A Windows
symlink-fixture privilege failure is skipped only for WinError 1314. The affected
22-test module passes (14 platform/privilege skips); Linux CI retains full coverage.
The numerical synthetic stack passed, with the complete export/watchdog and Ravel
source preparation still active.

## 11 October 2026 — reusable manual SQLite checkpoints

Implemented stdlib backup/restore on reviewed base
`c8ab57024b355314a3a84c8400093a173aa9f3f1`. Twelve focused portable tests cover WAL
consistency/source preservation, trusted identity/hash/schema anchors, strict
archive members/CRC/corruption/expansion, destination reuse, bounds and no active
ledger construction. POSIX permission/symlink assertions are explicitly scoped.
Full suite: 114 tests passed; validator passed. A small actual JobLedger snapshot
restored one synthetic queued job and zero attempts read-only, with source main/WAL
bytes unchanged and `REQUIRES_OPERATOR_RECONCILIATION`. No Docker/Drive probes,
scientific dispatch, tokens or policy changes. Receipt is in
`records/manual-checkpoint-integration-20261011.json`. Product-tool transport,
operator reconciliation/freshness, separately protected capsules and per-job
coordinator integration remain external; backups/hashes are not shared locks or
authentication. Deadline checks are cooperative, not an OS-stall watchdog.

## 2026-10-11 — Root review and approved NCBI publication

Published the owner-approved single NCBI host without changing the d031cef baseline,
privacy, secrets or analysis-container isolation. Fresh cloud HEAD passed at the
new catalog version; effective host enforcement was not independently exposed.
The earlier proxy 403 remains recorded. See records/cloud-ncbi-20261011.json.

Reviewed 07c5756 checkpoint code and CI. Windows found a test fixture whose SQLite
context manager committed but did not close the connection. Explicit closing fixed
temporary-file cleanup: 12 targeted tests pass, one symlink-privilege skip. No
checkpoint, gate or recovery semantics changed. The Ravel draft remains under
review; runtime checks do not establish scientific results or acceptance.

## 2026-10-11 — Bounded transfer and pilot review handoff

The private 16 MiB payload/archive roundtrip passed with one upload, owner-only
metadata and SHA/CRC verification. A new manual P001 coordinator ledger checkpoint
also passed private readback and read-only restoration, with zero scientific
attempts. Locators remain ignored. Ravel PR149 records independently reviewed
draft contracts and a passing full Windows governance check. Git dependency
qualification remains a real execution hold; no gate was bypassed.

## 2026-10-11 — Qualified Git image, explicit export hold

The initial APT failure came from passing the outer-only proxy hostname into an
inner container. Preserving Docker client proxy defaults and mounted CA trust fixed
package acquisition without changing hosts or routing. The worker verified three
signed Debian indexes, 31 package hashes and 61 wheels, then built offline. The new
image passed numerical, committed-source, runner and launcher-loss checks; see
records/numerical-git-runtime-20261011.json. Root has the completed report; independent
archive readback remains pending.

Automatic approval review rejected the partial-evidence Drive upload because
relayed authorization was not treated as a trusted human message. Further uploads
stopped. A sanitized 156,333-byte final qualification package is prepared and root
requested direct user approval for that exact export to the existing owner-only
folder. No biological dispatch, frozen contract, gate change or claim promotion.

## 2026-10-11 — Exact export approval did not cross the worker boundary

The owner approved the final 156,333-byte archive and existing private destination
in the root chat. The single child upload attempt was denied: automatic review
classified the forwarded approval as untrusted transcript evidence. No upload,
remote locator or readback exists. Pre-upload identity, ZIP/manifest and owner-only
folder checks passed. Preserve the qualified image/archive; no alternate route or
retry. The direct worker chat was opened for the owner to submit authorization.
Scientific dispatch and contract freeze remain held. Documentation/receipt-only
update; previous runtime/tests remain valid and no analysis was rerun.

## 2026-10-11 — Runtime export verified; metadata preparation resumed

Direct owner approval in the executing worker resolved the upload boundary. One
upload and worker readback succeeded; root independently verified raw bytes, ZIP
CRC, 28 member hashes and owner-only metadata. The exact runtime archive is now
bound in Ravel90c02ba with a frozen metadata-only contract and passing unchanged
governance checks. Mir remains sole coordinator and is preparing the per-job
packet/checkpoint. No real-input computation is yet claimed. Earlier denials and
runtime failures are retained; no validator or access control was weakened.

## 2026-10-11 — First metadata attempt and bounded artifact splitting

Root independently verified the before-dispatch checkpoint and released one
metadata attempt under Ravel90c02ba. The completed worker report records successful
archive/member hashes, three-library sparse integrity, 190.460 seconds and cumulative
945,848 KiB peak RSS. Result bytes remain unreviewed by root: automatic review blocked
the new exact evidence export; the earlier direct approval covered a different file.
No retry or scientific promotion. Preserve EXPORT_HELD and the after-run checkpoint.

Added a separate local multipart helper with external whole-file/manifest anchors,
fixed bounded parts and verified reconstruction. Eight focused tests passed,
including the actual 16 MiB boundary. No Drive upload implementation, numerical
pipeline, activation policy or scientific gate changed. Cloud multipart qualification
and the descriptive pilot remain open.

The after-run EXPORT_HELD ledger checkpoint subsequently passed coordinator
upload/readback/restore and independent root byte/ancestry/integrity/one-attempt
state checks. The numerical evidence archive itself remains unexported. No attempt
was retried, released or promoted to completed. Direct worker approval was requested.

## Metadata evidence review — 11 October 2026

Codex independently retrieved the owner-approved evidence export and checked all
46 manifest entries, nine exact source blobs and the Ravel receipt. Recorded the
observed sparse-memory prerequisite and completed descendant checkpoint; no
scientific method, gate, authority flag or acceptance changed. Earlier rejected
export and held checkpoint remain visible. Figure1 and multipart transport remain
separate qualification steps. Private storage/runtime locators stay ignored.

## 2026-10-11 — Capacity correction and preserved Figure1 preparation holds

Codex corrected the oversized 20 GiB host assumption against official Pro specs
(16 GiB VM), recorded the owner-selected 8 GiB operational amendment and verified
its passing memory check. Original frozen scientific files remain unchanged.
The bounded mount-placeholder repair succeeded; disk capacity then held both
preflight containers before start. Read-only accounting identifies VFS copying
as a likely cause and insufficient build cache. No cleanup or analysis occurred.
Current records distinguish the proposed container retirement from approval and
retain original source/input checks, failure receipts and checkpoint ancestry.

The owner subsequently approved scoped retirement. Both no-unique-data audits
and checkpoint ancestry were reviewed; both exact containers were retired and
the second passed offline preflight once. Recorded cgroup-v2 false/null field
normalization and missed short-run PID polling explicitly. Recovered about 4.2 GiB
without changing resource limits or scientific files. Numerical release still
awaits final packet, container controls and verified before-checkpoint.

## 2026-10-12 — Single Figure1 run and retained export hold

Codex reviewed the immutable packet and recorded container inspection, including
71 exact source blobs. A stale live coordinator database caused release suspension;
after read-only checkpoint recovery and worker reconciliation, explicit operator
recovery established a new active copy for the same coordinator. Root verified
the recovery checkpoint and preserved its exact prior event prefix.

The worker then executed the original Figure1 container once under unchanged
methods and the approved 8 GiB cap. It reports exit 0/no OOM, 196.03 seconds and
2,448,296 KiB peak process RSS. A new evidence export was rejected by automatic
review because prior approvals covered different archives. No successful upload,
retry, rerun or scientific acceptance occurred. Root independently verified the
descendant EXPORT_HELD checkpoint, not yet the scientific result archive. Current
docs and roadmap now distinguish reported execution from verified results.

The owner then approved the exact Figure1 payload directly in the existing worker.
Its local archive/part recheck passed, but the cloud turn stopped at a usage limit
before a complete verified transfer. Approval is retained; resumption requires
original-worker and per-file/remote-outcome reconciliation, not an analysis rerun.
The local Codex usage endpoint reporting availability does not clear the observed
cloud-specific failure. No account switch, purchase or quota workaround was made.

## 2026-10-12 — Backend map and main-branch integration

Codex added the requested root README deployment diagram and responsibility table.
It distinguishes GitHub repositories, dot coordination, bounded Codex Cloud compute,
private Drive checkpoints, operator review and human scientific authority. The
diagram labels the selected manual route without claiming unattended execution,
completed Figure1 export or a Google Cloud Platform deployment.

GitHub inspection found PR #2 merged into the former PR #1 base after PR #1 had
already merged to main. A scoped branch preserves the PR #2 merge and integrates
current main without conflicts. No frozen source, scientific contract, output,
runtime gate or acceptance decision changed. Private service-account identifiers
remain outside public documentation.

The owner-requested continuation was admitted after coordinator-ledger reconciliation.
The worker uploaded two parts before another runtime disconnect, reported complete
readback for part 0000 and incomplete materialization for part 0001. Root independently
verified both remote sizes, parent and owner-only permissions, not the bytes. No
renewed quota refusal was observed. The same attempt remains held with 24 parts and
the transfer manifest still unuploaded. No repeated retry or biological rerun occurred.

## 2026-10-12 — Same-worker export recovery and independent verification

At the owner's request, Codex and the existing coordinator reconciled the held
attempt and six uploaded parts, preserved the optional streaming proxy-403 probe,
and completed only missing transfers through the qualified Drive connector route.
Standard-input materialization avoided oversized shell commands. No analysis or
source was rerun/changed, no account or network policy changed, and sharing stayed
owner-only. Independent root downloads verified every part, full reconstruction,
ZIP CRC, all 99 member hashes and the unchanged original numerical run receipt.
Three descendant checkpoints preserved exact event prefixes and the same two
scientific rows; the final 30-event checkpoint passed fresh read-only restoration.

Current README, handoff, roadmap and environment summaries now distinguish verified
artifact integrity from pending QC/figure interpretation and scientific acceptance.
No frozen contract, runner, validator, analysis output or canonical claim changed.
Documentation validator and diff-whitespace checks passed; no numerical tests or
scientific runs were repeated for this status-only change.

## 2026-10-12 — Choi scientific review without a numerical rerun

At the owner's request, Codex reconciled the recovered original outputs with the
saved H5AD, visually inspected all five figures and compared with the audited
paper Fig. 1/S1 and methods. The 1,497 read-only assertions passed. Ravel owns the
full assessment; Weft records review provenance, absence of a new RQ proposal
and remaining publication/integration conditions. pAT2 absence, exclusion and
resolution sensitivity, DATP subcluster retention and figure-presentation limits
are retained. The local audit reader required nullable-string decoding before
it completed; no source output changed.

Current handoff, README, pilot/environment and roadmap status now distinguish
completed review from human acceptance and complete-output publication. Historical
source/transfer records remain dated. No frozen pins, ledger, reservation, analysis,
canonical questions, gates or acceptance policy changed. Offline validation passed (89 local links, 15 unchanged pins, scientific execution
disabled), as did diff-whitespace checks. The large-H5AD publication route remains
unqualified.

## 2026-10-12 — Backend-first roadmap refinement

The owner questioned prioritizing integration of the already-reviewed Choi paper
over automated discovery/screening. Codex inspected the actual CLI/modules and
gate specification and documented the implemented/manual boundary. The roadmap
now prioritizes a bounded discovery-to-candidate-digest backend, with separate
reading, dataset-eligibility and RQ-compatibility records. Choi publication remains
an open parallel track. The earlier serial implication that Choi must merge before
frontend qualification is superseded; its evidence and historical plan remain.

This is a development plan and source audit, not implementation of an autonomous
gate engine, activation of recurrence or a human scientific decision. No policy,
source pins, runtime gates, ledger/reservation or scientific outputs changed.
Documentation validation passed: 93 local links, 15 unchanged Ravel pins and
scientific execution disabled. Diff-whitespace checks passed.

## 2026-10-12 — Batch coordination and screening interface

Codex implemented the existing-adapter batch coordinator and pull-based agent
interface, with immutable specs, bounded date partitioning, explicit reconciliation,
OS locks, current-state/hash checks, strict proposals, XML attempt limits and a
retained digest. New tables extend the discovery catalog; no Choi scientific state
was mutated. The live development batch and private local byte/SQLite restore
check are recorded in docs/BATCH_PILOT_20261012.md. Tests exposed a malformed raw-
observation exception and excessive output; both were corrected without changing
scientific authority. B1/B2 mechanics are reviewable, not human-accepted gate policy.

The unchanged source query surfaced dental alveolar matches; no retrospective
query edit hid them. Five lexical paper/RQ links are a software exercise, not a
ranking evaluation. XML was inspected only within the recorded text scope. Cached
absolute reading paths restrict cross-host restoration; qualify an explicit
adapter and the selected cloud handoff before deployment. No paid API, credential,
schedule, cloud dispatch, Ravel evidence promotion or biological analysis occurred.

Linux CI verified code revision `5915ba7`: all 144 tests passed without skips,
with 105 documentation links and 15 unchanged source pins. PR #5 remains open
and stacked on PR #4; no human acceptance or merge is inferred from CI.

## 2026-10-12 — Portable reading paths; cloud qualification held

Codex replaced host-specific batch reading addresses with store-relative references
and added a verified, atomic legacy-address amendment. Private events retain the
previous result; source XML, receipts, packet hashes and scientific decisions are
preserved. Consumers now use a presentation-only resolved_directory. Tests cover
both path syntaxes, source binding, stale/foreign locations and restore reuse.
The actual 34-file development checkpoint recovered under two local roots with
one addressing event and no network retrieval, reread or numerical rerun.

The existing worker performed read-only readiness checks. GitHub and the owner-only
Drive connection remain available, but Europe PMC's host is not allowed and the
managed-runtime readiness tool was unavailable. No alternative backend, proxy,
new credential, policy edit or Choi-state mutation was attempted. The exact
single-host proposal and remaining qualification sequence are reviewable in
docs/SCREENING_CLOUD_QUALIFICATION.md; the owner's access decision remains pending.

Linux CI passed all 154 tests without skips on portability revision `1945515`;
PR #6 remains open and stacked on #5. Documentation validation passed 111 links
and 15 unchanged pins. The owner approved adding only www.ebi.ac.uk;
publication and actual worker-policy verification are recorded separately.

Owner-approved single-host amendment published through the verified existing
private weft-pilot UI; only www.ebi.ac.uk was added. Setup/startup d031cef,
package-manager preset and ftp.ncbi.nlm.nih.gov were preserved. Same-worker
effective policy remained old at 18:08:51 KST, so no network request or screening
dispatch was attempted. Proposed a separate screening-only task on the updated
existing environment and requested the owner's deployment decision. Choi and
all existing artifacts remain untouched. No new task or runtime reset.

The owner subsequently approved one screening-only task on the updated existing
environment. It was created and reported current enforced host policy, a clean
d031cef baseline and the verified private Drive destination. Initial normal-proxy
GET failed; sandbox-versus-platform diagnostics are in progress. Existing Choi
worker and artifacts were preserved; no live batch or upload has started.

Readiness correction: earlier proxy/socket failures came from the default
restricted command sandbox. A reviewed request through inherited proxy/TLS
succeeded; no platform outage established. The isolated 1945515 source passed
73 cloud tests/111links/15Ravel blobs. The cloud batch returned 82 observations,
74 papers/148 links and one pending packet, with no assessment or XML read.
An unknown-payload preparation/upload handoff was rejected by automatic approval
review. A safer local-only preparation passed a 20-member inactive restore;
exact 389137-byte archive b4dff329... now awaits direct owner export approval.
No rejected export was retried or bypassed. Screening and remote recovery remain
unqualified; Choi is untouched.

The owner directly approved the before archive; worker readback and independent
root Drive/CRC/20-member/SQLite/pending-packet verification passed. Root released
the frozen five-link pass: one read next, one hold, three link rejections, 143
deferred; one XML/four statements held for further source review. Worker-local
recovery made zero retrievals and no duplicate events. All stores quiesced.
Exact after archive is 522632 bytes/SHA7edfa55a.../42manifest members; direct owner
export approval requested because the before approval does not cover it. This
is operational evidence, not semantic accuracy or scientific acceptance.

## 2026-10-12 — Manual cloud screening recovery qualified

The owner directly approved the exact after archive. Worker upload/readback and
independent root download verified 522632 bytes, SHA7edfa55a..., all 42 members,
SQLite integrity/counts, original eight-event prefix and 17 unchanged source files.
A fresh Windows verification copy replayed completed searches, five saved
responses and one cached XML assessment without HTTP, duplicate events or changed
rows. All portable paths resolved within the restored store. An initial sandbox
path-access denial was preserved and resolved by normal execution permission on
a fresh copy; no source/evidence modification or alternative egress was used.

This closes the manual B2 handoff and B4 recovery component, not semantic quality,
full B4 source coverage or unattended deployment. Private locators/receipts stay
under ignored runs; current public status now records the observed qualification.
Choi, Ravel acceptance, source pins and scientific outputs are unchanged. No
biological rerun, new host/service, schedule or merge. B3 coverage/data/RQ records
and independent screening evaluation remain next. Existing 154-test Linux code
validation remains applicable: this closeout changes documentation/evidence only.

Closeout validation passed: 112 local links, 15 unchanged pinned Ravel files and
Git whitespace checks. Refetched main b59ed911 and integration base #5 at 827ad51b
remain unchanged. GitHub identity verified as xorca0711 and Git author as Xorca.
A final preservation-only worker message was blocked because tool approval was
unavailable; the completed transfer already reported all stores inactive, and
the block did not invalidate verification or authorize new work.

## 2026-10-12 — B3 coverage and separate data/RQ proposal records

| Date | Item | Proposed by | Decided by | Decision | Reason |
|---|---|---|---|---|---|
| 2026-10-12 | Next backend stage: B3 evidence qualification interface | Owner requested roadmap progression; Codex designed and implemented | Owner authorized implementation; detailed validator semantics and merge await PR review | Implement additive proposal records and test preserved cached evidence | Separate what was inspected, suitability for a stated use and RQ fit without granting scientific authority |

Codex added `weft/qualification.py`, four batch CLI commands, status/digest
integration and 16 focused tests. The existing catalog receives additive packet,
artifact and immutable review tables; no old source, reading decision, gate or
scientific ledger is rewritten. Local artifact bounds are operational intake
limits. Actor identity, actual viewing and semantic support remain uncertified.

Tests cover captions versus pixels, missing material, unknown/pooled units,
absent perturbation controls, endpoint mismatch, duplicate accessions, stale
metadata, source/artifact tampering, linked files, authority escalation, amendments
and recovery. The first targeted run found two test-fixture aliasing failures:
editing a response also edited the expected returned template. Deep-copying the
fixture fixed the test; production checks were not weakened. Full Windows run:
168 tests passed with 24 platform skips; the expanded focused run passed 16 tests
with one symlink skip. Linux CI verifies the final 170-test suite.

The cached after-screening archive produced six figure/two supplement entries and
two held proposals in an inactive development copy. No materials were newly
inspected, and no network or analysis ran. The original source/checkpoint and
screening history stayed intact. Record replay and another-root recovery passed.
Public records contain compact hashes/counts only; full text, review packets,
private locators and copies remain under ignored runs. B3 cloud qualification,
actual B4 material review and B5 independent evaluation remain open. Choi is
untouched; no new access, deployment, schedule or merge was performed.

Linux closeout: all 170 tests passed with no skips on 11affb4; both PR and
push CI succeeded. Documentation validation passed 119 local links and 15
unchanged Ravel pins. PR #7 is open and ready for explicit code review, stacked
on #6. GitHub author is xorca0711; Git author/committer is Xorca. No merge.

## 2026-10-12 — B3 cloud qualification and bounded B4 access hold

| Date | Item | Proposed by | Decided by | Decision | Reason |
|---|---|---|---|---|---|
| 2026-10-12 | Qualify PR #7 in the existing worker, then bounded B4 source review | Owner requested scope; Codex coordinated | Owner authorized execution; scientific acceptance and merge remain unissued | B3 qualified; B4 stopped before material acquisition | Preserve Choi and stop at new access/deployment decisions |
| 2026-10-12 | Add only europepmc.org to the existing environment | Codex requested the specific documentation host | Owner explicitly approved | Approved but not published | Saved browser-control permission blocks chatgpt.com, including after renewed authorization |

The existing worker verified source d95d558, 55 targeted tests, 119 links,
15 Ravel blobs and all 42 members of the preserved after-screening checkpoint.
Disposable B3 proposal and fresh-path recovery checks retained source bytes,
screening decisions and the original 20-event prefix. Both data-use/RQ proposals
are held; no source material was newly inspected. The designated B4 store remains
unchanged, and all stores are quiesced. Root reviewed these receipts and the pinned
A0 result/dossier; no independent second cloud test or scientific acceptance is
claimed. The public check record excludes private worker paths and identifiers.

The B4 API-documentation probe used two allowed EBI requests (both HTTP 404,
248 bytes total), establishing an unresolved documentation dependency rather
than a failed material download. Original WEBP figures and DOCX supplement are
not directly supported by B3 intake. Proposed viewing conversions need explicit
provenance and verification; extraction alone would remain partial DOCX review.
No format validator was weakened or renderer installed. Browser permission
enablement and then effective-policy verification are the exact next dependencies.
No alternate control route, new worker, analysis, private export, schedule or merge.

Local closeout validation passed 124 documentation links, all 15 unchanged pinned
Ravel blobs and Git whitespace checks. Main b59ed911 and the PR #7 integration
base d95d558 were refetched and unchanged. Runtime code is unchanged, so the
existing full-suite CI and new 55-test cloud evidence remain applicable. GitHub
identity was verified as xorca0711; author/committer is Xorca.

## 2026-10-12 — Existing-worker policy adoption check

The owner reported publishing the approved single-host amendment and requested
verification, explicitly requiring a stop if a new worker is needed. The same
screening worker obtained fresh managed status: current running/connected state,
restricted/enforced policy, desired/observed revision 24 and unchanged configuration
version. europepmc.org remains excluded. No supported in-place adoption control
is exposed. This establishes the old worker's effective policy; it does not
independently verify the reusable environment's newly published configuration.

B4 stopped at that deployment decision. No new request, worker, material, proposal,
upload, scientific run or Choi action occurred. The existing stores and original
two-request usage are preserved. PR #8 records the receipt hash and the exact
conditional checkpoint-restoration path; no new deployment is authorized by this
documentation. Root reviewed the existing worker's report and saved receipt hash.
