# Current project state

Update this before stopping work, every session.

## Phase 4 critic-assisted review — 20 October 2026

The owner requested phase 4 and chose to be the primary human reviewer after a
substantial critic-AI review. A separate critic audited the evaluation contract
and two exposed, non-B4 cases, then reviewed the new handoff implementation.
**Human adjudication is pending; independent scientific-quality evaluation has
not been completed.** See the [review guide](docs/PHASE4_SCIENTIFIC_QUALITY_REVIEW.md)
and [bounded checkpoint](records/phase4-development-review-20261020.json).

Freshly fetched main is `d14961f5e57c2ff61d0c3d5233be14706ac024be` (PR #13);
its main CI passed. Work uses `codex/weft-independent-evaluation-20261020` in the
existing scoped worktree. Ravel and live pilot catalogs/workers remain unchanged.

- Added a private `quality-review-export` route for explicitly AI-assisted,
  exposed development adjudication. It validates source hashes, exact DOI and
  JSON locators, retains original critic findings and separate human answers,
  preserves partial/disputed answers and emits no independent quality score.
  Blank templates contain no inferred human answers. Copies remain portable;
  previous outputs are not overwritten. No model or live-store call is added.
- Corrected the critic-confirmed evaluator defect where an unblinded reference
  could enter `declared_unseen` if exposure attestations said `none`. Such records
  now remain exposed. Independent-reference requirements were not weakened.
- Critic review found and the implementation fixed lost nested source paths,
  human corrections hidden from the rendered view, and Windows reserved-name
  aliases that could overwrite a source snapshot. Focused regression cases cover
  each, including uncertainty and absent human labels.
- Prepared private `runs/phase4-review-20261020/human-handoff-v2/`: two retained
  metadata snapshots, readable cards, an empty human response template, report
  and manifest. Eight critic findings and six dimension labels await the owner.
  Two exact DOI metadata requests were made; no figures, supplements, dataset
  files or numerical analysis were requested. Primary web checks were limited
  to the two non-B4 article pages. This is a purposive retrospective check,
  not an unseen sample or a source-complete B3 assessment.

Local validation: the full suite passed **317 tests: 292 passed, 25 existing
platform skips**. The final JSON-type guards and added case then passed all
**13 handoff tests**; the unchanged evaluator suite had passed 11 tests. Offline
configuration/documentation validation and whitespace checks passed. Linux CI
provides the final full-suite result on the integrated code. No scientific pass
or sample-size/threshold authority is inferred from these software checks.
The optional browser preview rejected the local-file protocol; no workaround
was attempted. Static rendering/source checks passed; interactive visual QA is
not claimed. The Markdown review cards provide a directly readable handoff.

Next required input is the owner's case judgments and reasons; unknown is valid.
Their critic-assisted answers will remain exposed adjudications, not independent
reference labels. A later independent benchmark still needs a reviewed sample,
source-complete evidence, genuinely independent references/bibliography and
prospectively chosen criteria. Do not redate old outcomes or reuse assisted labels
as blinded evidence. Current Ravel dossiers were not read.

B4 `10.1002/advs.77773` / `PMC13634473` was excluded entirely; no retry or reroute.
Choi remains closed, M6 disabled and cloud-launch mapping/runtime capability
unqualified. No access changes, external messages, schedules or live dispatch.

## Phases 1–3 implementation and integration — 20 October 2026

The owner authorized these phases without a work timeline. Coordinator PR #12
is merged at `4f8fa5978822da12b707abc9b79b616d4fe3b671`; both PR checks and
[main CI](https://github.com/xorca0711/weft/actions/runs/39348519577) passed.
The older entry below describes its pre-integration checkpoint. The extension
uses scoped branch `codex/weft-selection-materials-20261020`. Freshly fetched
main has the same tree as its phase-1 parent; no intervening source change.

- Phase 2: new workflows freeze `paper-stream-v1` nominations, rotating query
  streams and admitting one RQ link per paper per round. Existing batch policy
  and integrity holds remain unchanged. Read-only audits compare the nominal
  legacy order, new order and actual issuance; an optional exact-key bibliography
  records its denominator, missing papers, provenance and prior exposure.
- Phase 3: verified same-batch XML reuse avoids another retrieval while creating
  separate RQ packets and assessments within the existing attempt cap. Local
  manifests bind resource IDs, bytes, hashes and origin, with preflight validation
  and exact retry after partial intake. Intake never records inspection.
- Private immutable review bundles link citations to source text and show source
  coverage, attachment verification/holds, data-use proposals and RQ compatibility
  separately. File copies are explicit opt-in. No source upload or URL retrieval
  is added. The existing scientific validators and authority flags are retained.

The synthetic demo in ignored `runs/phases-1-3-demo-20261020-v2/` completes four
reading packets for three papers using three XML fixture calls and one verified
reuse. Both B3 proposals remain held and the supplied fixture remains uninspected.
The fixture's nominal legacy cap reaches two papers. This is exposed synthetic
mechanics evidence, not a real-world ranking, recall or scientific-quality result.
The local rendered view and exact citation navigation were inspected; prior demo
exports are retained as immutable checkpoints. Reproduce using `workflow-demo`
with a new directory; see the [guide](docs/SELECTION_AND_MATERIAL_REVIEW.md).

Review found and fixed the shared argparse default affecting legacy discovery,
and a cached-file change window between checking and copying. Regression tests
cover both. Source reuse, manifest interruption, caps, held/tampered material,
frozen-plan integrity, escaping and review manifests have targeted coverage.
Local delivery checks: **304 tests: 279 passed, 25 existing platform skips**;
offline validation passed (225 local links, 15 pinned files). Whitespace checks
passed. Integration will use the fetched main base and exact reviewed head;
the PR/main checks provide the Linux result separately from these local checks.

No live source query, scientific analysis, cloud task, hold retry, permission
change or support submission occurred. Ravel and live pilot catalogs/workers are
unchanged. Choi closed, B4 held, M6 disabled. CLI environment mapping, native
runtime capability and exact delivered-prompt binding remain unqualified; the
browser allow/denial discrepancy remains unresolved. No platform repair claimed.
After engineering integration, the next separate phase is independent quality
evaluation with an explicit reference bibliography and exposure record. Live
launcher qualification still needs new supported platform evidence; do not retry
or reroute existing held work.

## Workflow coordinator implementation — 20 October 2026

Implemented the owner's requested coordinator, integration/recovery tests and
status/export view on `codex/weft-coordinator-20261020`, using the existing Weft
worktree. Ravel and the live pilot stores/workers were not changed. Fetched main
before implementation and again before delivery; HEAD and origin/main both remain
`4b9215ceaa72d75bfc62a323ed9f0c22dbf4bbbf` (PR #11 is merged).

- New manual-pull workflow composes the existing batch, handoff, reading and B3
  validators. It saves responses before ingestion, supports exact saved-return
  recovery, requires explicit bounded retrieval, and never releases holds or
  invokes a model/cloud launcher. Only fresh unstarted dedicated catalogs opt in.
- Read-only status and private immutable JSON/HTML exports distinguish discovery,
  reading and evidence-review completion, cap deferrals, data/RQ proposals,
  coverage gaps and source/actor context. Restored catalogs remain inactive for
  mutation; existing pilots can be viewed without adoption or continuation.
- Dated platform constraints remain separate: CLI environment mapping is
  unverified; the admitted native child lacked runtime-status capability; the
  loaded browser allow rule conflicted with its denial. A platform integration
  mismatch is an inference, not an established cause. The owner reports granting
  requested access; no repeated access request, new probe, retry, fallback,
  privilege change or support message was performed. Choi closed, B4 held, M6 off.

Validation: **281 tests: 256 passed, 25 existing platform skips**, including all
25 new workflow tests; offline validation passed (15 pinned files). Initial
read-only export tests exposed a missing SQLite URI-mode flag; it was corrected
before these passing checks. `git diff --check` passed. The synthetic status demo
is in ignored `runs/workflow-demo-20261020/`; it is not a live pilot result.
No biological analysis or live cloud test was run.

See the [coordinator guide](docs/WORKFLOW_COORDINATOR.md) and
[integration tests](tests/test_workflow.py). Implementation is local and ready for
code review; no deployment or scientific qualification is claimed. Next: review
the coordinator change; obtain supported environment mapping/runtime-capability
evidence before any separately authorized launcher qualification. B4 continuation
and independent semantic evaluation retain their existing holds/dependencies.
The earlier planning entries below remain historical.

Same-session roadmap clarification: grouped the remaining work into baseline
integration, discovery/selection quality, material/evidence review, independent
evaluation, cloud-adapter qualification, remote ownership/recovery, general
scientific-job/evidence handoff, and separately authorized recurrence. These are
dependency phases without a timeline; existing M/B/L identifiers remain intact.
Offline selection/material tooling and evaluation preparation can proceed while
platform qualification is held. Live B4 is not resumed or replaced, B5 execution
retains its access/launcher prerequisites, and Ravel integration waits for the
owner's reinitiation. This clarification changes only this progress note; prior
software checks remain valid and were not repeated.

## Technical development assessment — 20 October 2026

The owner requested an engineering backlog without personal timelines. Current
main remains `4b9215ceaa72d75bfc62a323ed9f0c22dbf4bbbf` after fetch.
Code inspection confirms separate batch/screening/evidence/handoff interfaces,
identifier-ordered candidate selection under screening caps, a compact digest,
and an existing offline evaluator. Component recovery fixtures already exist.

Proposed implementation priorities: compose the existing interfaces into a
resumable bounded workflow; extend integration failure tests across stage
boundaries; add an explicit versioned candidate-selection policy; improve material
preparation and evidence navigation; expose the existing evaluation and event
records in useful review/error reports. Reuse the existing store and validators.
New selection or workflow semantics require their normal explicit review; no
scientific admission authority is added. These are proposed changes, not completed
features or a directive to reprocess held material.

Offline orchestration, fixture adapters and review exports can be developed
without claiming live launcher qualification. Live dispatch, B4 continuation,
unattended hosting and recurrence retain their existing access/review dependencies.
No code, runtime setting, scientific result or schedule changed. Only this local
progress note was edited; whitespace validation applies and runtime tests were
not repeated. Ravel research remains awaiting owner reinitiation.

## Development priority clarification — 19 October 2026

The owner requested focus on substantive project development. The immediate
gap is a bounded fresh-paper workflow whose scientific judgments and operational
recovery have both been evaluated. The earlier evaluation-design proposal is
preparation for that milestone, not the milestone itself.

Existing batch, screening, B3 proposal, handoff and evaluation interfaces should
be reused. The next implementation review should identify the missing connections
from one explicit trigger through permitted material review, separate reading /
data-use / RQ-link decisions, a complete digest and independently verified restore.
Qualification must preserve failed, rejected and held items; source hashes alone
cannot establish citation support or biological-unit correctness. Evaluate against
independent reference judgments and an explicit comparison bibliography, recording
prior exposure and operator interventions. Sample size, criteria and reviewer
authority remain to be settled before an actual evaluation; no pass is invented.

Native L1 access and B4 remain external blockers. Do not retry or reroute either
hold. Their resolution and interrupted-state reconciliation precede any dependent
live continuation. Offline integration work may proceed within its own scope;
it cannot qualify live enforcement, distributed ownership or scientific quality.
Recurrence follows this bounded operational/quality milestone. No new deployment,
scientific gate, schedule or analysis was implemented by this assessment.

Main remains `4b9215ceaa72d75bfc62a323ed9f0c22dbf4bbbf` after fetch. Inspected
the current roadmap and batch/screening/handoff/evaluation interfaces; no runtime
tests repeated for the progress-only clarification.

## Read-only portfolio reconciliation — 19 October 2026

Freshly fetched main is `4b9215ceaa72d75bfc62a323ed9f0c22dbf4bbbf`,
the merge of PR #11. Earlier statements below that PR #11 remains unmerged
are historical. Review used a separate scoped worktree; the original checkout
and its ignored operational records remain preserved. The intentional Ravel
pin remains `bfe26b876221cf6c6fa6f9b16a90cfb516b5998d`; it is not a claim to
track current Ravel main.

The [completion review](docs/ROADMAP_COMPLETION_REVIEW_20261013.md) still
distinguishes implemented offline controls from scientific and operational
qualification. All 32 RQs have configured profiles, but the 30 newer drafts
remain unqueried. Choi remains a completed descriptive discrepancy benchmark;
independent screening evaluation remains open. L1 runtime access and B4 remain
held, interruption state unresolved, and M6 disabled. No hold was retried.

Proposed next package: prepare a small, review-ready reading-evaluation design
that serves Ravel's actual reading backlog. Specify source/version coverage,
exposure, separate reading/data/RQ judgments, independent reference review and
denominators using the existing [B5 requirements](docs/B5_EVALUATION_PREPARATION.md).
Do not call an exposed development set independent evaluation. A real sample,
reviewer and acceptance criteria remain to be agreed after the documented
launcher/review-access dependencies are qualified. No replacement B4 review,
new cloud job, model call, deployment, support message or schedule is implied.

Verification is limited to current-base/state inspection and the progress-only
diff; existing runtime tests are not repeated. Next: reconcile the merged-state
wording in current navigation and prepare the bounded design for review. Platform
integration review, B4 resolution, independent scientific labels and remote
ownership/recovery qualification remain external dependencies. Personal planning
is retained outside the public repository.

## Partial-stage implementation review and hold retries — 13 October 2026

Three owner-authorized review agents completed bounded discovery,
screening/evaluation and launch-control work. Root integrated the CLI and
reviewed discovery; the controls agent independently reviewed reading gate and
evaluation changes. The [completion review](docs/ROADMAP_COMPLETION_REVIEW_20261013.md)
records the phased remaining jobs and limits.

- Correction/retraction links now hold affected current candidates across
  retrieval order while preserving decisions and receipts. MED/PMC self-ID
  conflicts and inconsistent paging fail conservatively; version links remain
  nominations rather than merged identities.
- Strict reading schemas preserve explicit holds. New offline `profile-coverage`,
  `evaluation-plan` and `evaluation-score` commands report configuration gaps and
  frozen-item accounting without model calls or scientific permission.
- Launch journals reject reused task IDs and inconsistent state/receipt/history;
  snapshot reads tolerate valid concurrent transitions. These are local controls,
  not distributed fencing or cloud persistence guarantees.
- The first audit found 2/32 RQs configured (A0/A1). The discovery reviewer then
  prepared 30 source-bound opt-in drafts for A2–A31, retaining the original two
  profiles. All 32 pinned RQs now have configuration coverage; the new profiles
  remain unqueried. No search recall or real B5 evaluation was measured.
- One newly authorized status-only follow-up per existing held worker: native
  child still reports no runtime-status capability and ran no tests; B4 was again
  rejected by the platform's biology-content restriction, with no completed status
  result. No alternate route or replacement worker was used. Private transcripts
  remain ignored under `runs/roadmap-completion-20261013/`.

Validation: final local full suite **256 tests, 231 passed, 25 platform skips**;
offline configuration/documentation validation passed with 15 pinned files.
Integration base was freshly fetched and remains `5cd4178af7cd706a51b8fb814f94c223c2fa32ab`.
Delivery targets [PR #11](https://github.com/xorca0711/weft/pull/11); its current
head checks record Linux CI separately from this local verification. It remains
subject to integration review. No Choi rerun, B4 review, cloud test, deployment,
support message, new export or schedule was performed.

Next: review corrected code/CI; obtain platform integration review for L1 and
resolution of B4's restriction before a permitted continuation; qualify the new
query drafts and freeze an independent B5 sample/reviewer/criteria. Remote coordinator
ownership, interruption/cancellation recovery and PC-off operation need their
own qualification. M6 remains disabled pending those results and an explicit
cadence/scope/usage/export decision. Choi M4/M5 remain complete and preserved.

## Same-child diagnosis complete; platform review pending — 13 October 2026

Root directly read the completed diagnostic turn. The child reports inspection
of 341 operations, 55 cloud skills across all pages and 0 executor skills: no
runtime-status tool, runtime skill or lazy tool-discovery route is exposed.
No explicit denial occurred; deployment/routing/permission cause remains unknown.
Root holds the completed report, not the raw catalogs. Tests remain unstarted.

Mir's owner-relayed comparison confirms the saved prompt and retained create
argument both match the frozen 4,673-byte value. The decoded child input is one
terminal LF shorter. No raw wire request exists to locate the transformation;
original bytes, spec, journal and receipt remain preserved. This formatting issue
is separate from the missing runtime capability and does not authorize retry.

The [diagnosis](docs/qualification/NATIVE_RUNTIME_HOLD.md), roadmap and unsent
[support request](docs/support/LAUNCHER_SUPPORT_REQUEST_20261013.md) are updated.
A private task/turn-ID addendum is prepared. **L1 remains partial/held for platform
integration review.** Do not resend either prompt, create a replacement, run tests
or weaken the gate. No worker message, settings change, upload or support message
was sent by root. Choi is closed, B4 held and M6 disabled.

Validation passed: 205 scaffold links, 15 source pins, 140 changed-document links,
JSON/privacy checks and Git whitespace checks. Private evidence/addendum remain
Git-ignored. Main was fetched and is unchanged. No runtime tests were rerun;
changes remain local.

## Native admission verified; same-child runtime HOLD — 13 October 2026

Mir reports one native create, acknowledged journal reopen and identical result
readback. Root directly read the resulting idle child/completed turn and verified
the original 3,165-byte HOLD receipt and empty log by SHA-256. The child fetched
no source and invoked no tests. Coordinator journal/catalog claims remain
owner-relayed, not independently read by root.

The [diagnosis](docs/qualification/NATIVE_RUNTIME_HOLD.md) identifies a missing or
undiscovered runtime-status integration, not a demonstrated allowlist failure.
The child's policy-file hash equals the earlier successful manual worker's
snapshot, but does not prove current enforcement or configuration version. Root
also found the exposed child input lacks the frozen prompt's final LF; all other
text matches. The responsible normalization layer is unknown. Preserve original
bytes and reconcile retained call evidence before calling exact binding passed.

Roadmap: **L1 partial** (admission and result recovery observed; runtime execution
held). A private `MIR_SAME_CHILD_DIAGNOSTIC.txt` is prepared for capability-only
inspection and original-call byte comparison. It has not been sent. No new task,
follow-up turn, settings change, test invocation, upload or schedule occurred in
root's verification. Do not paste the original launch prompt again. Choi remains
closed; B4 held; M6 disabled. PR #11 remains unmerged.

Validation passed: 203 scaffold links, 15 source pins, 144 changed-document links,
JSON/private-identifier checks and Git whitespace checks. Private records remain
ignored. Main was fetched and remains unchanged; no runtime code/test changes.
Changes and the support request remain local; no support message was sent.

## Native synthetic packet prepared — 13 October 2026

The owner confirms that `weft-pilot` is selectable in the same workspace and
manual launches have already been tried repeatedly. The picker check is settled;
do not request it again. Account scope remains owner-attested rather than a
new authenticated account inspection. Earlier missing-observation notes below
are historical and superseded by this update.

The [new trial](docs/qualification/NATIVE_SYNTHETIC_TRIAL.md) has a self-contained
private prompt for the existing **Mir** chat, including the exact saved target,
worker text/hash, PR #11 source pin and single-submission journal sequence. It
qualifies one native creation/acknowledgement/result path with 12 launch-journal
fixtures, not the completed manual 18-fixture trial. Root reviewed the scoped
source and passing CI at `824c562d5d0140aecadd35023fbaecca303ef126`; runtime/test
code is unchanged. PR #11 remains open. Main is still
`5cd4178af7cd706a51b8fb814f94c223c2fa32ab` after fetch.

Next: owner pastes the prepared prompt into Mir; Mir verifies the live exact
target, persists intent in its own coordinator workspace and submits at most once.
The child must verify actual policy/version before tests. Return the real task
acknowledgement and verified outputs, or the precise hold. Root has launched no
task, created no journal and sent no worker message. Choi stays closed, B4 stays
held, and M6 stays disabled. This is no claim of restart retention or deployment.

Validation passed: 201 scaffold links, 15 source pins, 137 links across changed
documents, packet/embedded-prompt hashes, static 12-fixture count, private-identifier
scan and whitespace checks. Private dispatch files are Git-ignored. Runtime/test
code matches the reviewed pin; no runtime tests were rerun. Changes are local.

## Environment-resolution triage — 13 October 2026

The environment-list screenshot shows **Private** in Sharing, not an Unpublished
badge. It also shows **Unknown repository**, contradicting the correct Edit/catalog
mapping. Supported read-only checks now confirm `xorca0711` for GitHub CLI login
and the connected GitHub app installation; both resolve the public, non-archived
`xorca0711/weft` repository on `main`. This does not prove the cloud connection or
identify the UI discrepancy's cause. No reset, reconnect or republish was attempted.

The [resolution sequence](docs/qualification/NATIVE_LAUNCH_INTERFACE.md) now uses
the same-account/workspace **New chat → Work in → Cloud** picker as the next
publication-availability observation, without submitting a task. If available,
retain the current environment and qualify the native synthetic route. If actually
unpublished, inspect and fix a demonstrated setup failure before republishing the
same environment. Persistent contradictory mapping belongs in the updated,
still-unsent [support draft](docs/support/LAUNCHER_SUPPORT_REQUEST_20261013.md).

CLI mapping and browser permission remain unresolved but are optional tracks for
native Mir delegation. Native admission, new-worker enforcement and remote
ownership/recovery remain unqualified; B4 stays held, Choi closed, M6 disabled.
No cloud job or account/configuration change occurred. Documentation checks apply;
runtime tests are not repeated for this explanatory update.

Validation passed: 198 scaffold links, 15 source pins, 88 links in changed
documents, targeted private-identifier checks and Git whitespace checks. Changes
are local; the support draft remains unsent.

## Mir native capability reconciliation — 13 October 2026

**L0 is partial.** The owner relayed Mir's 05:07:22–05:07:52 UTC report: native
`environmentConfigId` selection and one catalog response for `weft-pilot` /
`xorca0711/weft`, with no creation call. Root independently compared the full
reported version and setup ref against preserved evidence: both match exactly.
The saved-ID prefix also matches the earlier CLI routing ID, but undocumented
prefix semantics do not prove Mir's current account/workspace. Raw identifiers
and the structured relay/comparison remain in ignored private run records.

The [interface mapping](docs/qualification/NATIVE_LAUNCH_INTERFACE.md) records
acknowledgement/continuation/status schemas, absent atomic version pin, and
unqualified cancellation/ownership. Root did not retrieve Mir's raw tool response
or gain its launcher capability. The next dependency is a read-only owner check
of the active AI-host account/workspace and current published environment/network
settings. The exact Settings → Codex Cloud → Environments → weft-pilot → Edit
path was supplied from official documentation; no save or republish is requested.

Check configured policy before a future authorized launch and actual worker
enforcement after admission, before tests. No launch, adapter deployment, schedule,
scientific gate change, Choi action or B4 continuation occurred. Current summaries
are synchronized; [sanitized receipt](records/native-launch-capability-20261013.json).

Owner screenshots subsequently confirmed the environment/repository, enabled
internet, Package managers preset, three additional hosts with `europepmc.org`
visible, Only me access and no listed secrets/variables. Copies and hashes are
preserved privately. A later expanded-domain screenshot confirms the full list:
`europepmc.org`, `ftp.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`. Configured-network
inspection is complete. Await current account/workspace and publication status;
do not infer either from the other observations.

Validation passed: **196 scaffold links, 15 source pins and 199 links across
changed documents**; the new receipt parses, public additions pass the targeted
private-identifier scan, and whitespace checks pass. No runtime code changed or
test/analysis run was repeated. These changes remain local.

## Remote automation architecture — 13 October 2026

The owner requested continuing the recommended stages and finding a fully remote
architecture. The [implementation sequence](docs/REMOTE_AUTOMATION_ARCHITECTURE.md)
now qualifies **native Mir delegation to existing `weft-pilot` first**, with CLI
compatibility optional. Official documentation describes PC-off dot work and
coding threads in existing cloud environments. That is product capability,
not proof of Mir's current tool access or unattended ownership/recovery.

L0's [read-only Mir capability check](docs/qualification/MIR_LAUNCH_CAPABILITY_CHECK.md)
was prepared for owner relay. At preparation, root's Mir read returned idle
metadata and no turns. The later owner-relayed report is reconciled above.
Root still lacks the environment-selecting launcher. No direct message or worker
was sent. Do not guess IDs, reuse the completed synthetic task or retry denied
browser actions.

L1–L4 specify exact synthetic submission, remote ownership/recovery, bounded
search/screening with independent B5 evaluation, and finally separately authorized
recurrence. Existing 200-test offline evidence is reused; no runtime change or
analysis rerun is needed for these documentation updates. The API/controller
contingency requires new access, hosting, storage and billing decisions; none
was made. Native delegation must respect the same permissions and scientific holds.

The roadmap, readiness note, backend plan, README and entry point are synchronized.
PR #11 is still open; diagnosis/support/architecture revisions are local. Choi,
B4 and M6 remain unchanged. See the [architecture record](records/remote-architecture-20261013.json).
Validation passed: **192 scaffold links and 15 source pins**; an additional check
covered all **203 local links in the changed documents**, including the new
architecture and relay prompt. The record parses as JSON, targeted privacy checks
found no private-identifier patterns in new public artifacts, and Git whitespace
checks passed. These are document checks, not native launcher qualification.

## Update check and support preparation — 13 October 2026

Prepared a [sanitized support request](docs/support/LAUNCHER_SUPPORT_REQUEST_20261013.md)
covering browser permission provenance and CLI/durable-environment compatibility.
The app's configured production updater reports **up to date**: version
`26.1007.21434`, build `13901`. Windows package inventory separately reports
`26.1007.2314.0`; both identifiers are attributed to their reporting interfaces.
PATH CLI and plugin app-server both report `0.162.0-alpha.17.2`.

The official changelog search index lists standalone CLI `0.162.1`, but the
fetched page did not expose that release for direct verification. No applicable
fix or compatibility with the app-directory CLI is established. Installed
`codex update --help` has no check-only mode; its documented update command can
apply changes, so no updater or installer was run. Ask support which component
and release support the existing durable environment before changing runtimes.

The request is prepared, not submitted. Account emails/IDs, task/environment
identifiers, local usernames, credential material and raw histories are omitted.
No support message, session export, browser retry, login, configuration change,
cloud job or scientific rerun occurred. Choi/B4/M6 are unchanged. The prepared
request and version evidence are saved locally on the existing diagnostic branch.
[Update-check record](records/launcher-update-check-20261013.json).
Validation passed: **184 local links and 15 source pins**, valid JSON record,
targeted draft privacy scan and Git whitespace checks. No runtime test rerun was
needed because this change contains documentation and diagnostic records only.

## Read-only launcher access diagnosis — 13 October 2026

[Diagnostic findings](docs/LAUNCHER_ACCESS_DIAGNOSIS.md): the supported CLI account
read confirms the designated AI-host identity. Its loaded configuration also
confirms the browser origin is allowed; the requirements read returns null.
However, active thread overrides are not inspected, and bounded desktop logs
did not expose the effective browser decision. The mismatch remains unresolved.

The CLI environment picker loads only its global option, with no named
environments. Its empty task list has no next cursor. It rejects the existing
synthetic worker ID with HTTP 404 / `Invalid task ID`, while the supported app
reader still finds that exact worker idle with its last turn completed. CLI
account identity is established; mapping to published `weft-pilot` is not.

Stopped at product troubleshooting for active-policy provenance and supported
CLI/durable-environment mapping. No task, inference, token inspection, login,
account switch, settings change, upgrade, support submission or new deployment
occurred. Private diagnostics remain ignored locally. Choi/B4/M6 are unchanged;
no PR was merged or cloud analysis rerun. See the diagnostic for exact next steps.
Offline validation passed **181 local links and 15 source pins**; Git whitespace
checks passed. Runtime and biological tests were not repeated for this
documentation-only diagnosis. The update is saved locally on the scoped
`codex/launcher-access-diagnosis-20261013` branch; no remote publication occurred.

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
