# W01: provisional evidence workspace, ownership and schema

Status: **design baseline adopted for delegated implementation, 21 October 2026**.
The owner requested continued roadmap implementation after this proposal. D01–D05
therefore guide the non-executing [workspace implementation](EVIDENCE_WORKSPACE.md).
No detailed human technical review or scientific design approval is claimed.
The original draft examples below remain proposal-only historical artifacts.
This document and its examples grant no scientific execution authority.
The current [Ravel contract](RAVEL_CONNECTION.md), [gate specification](GATES.md)
and disabled [policy](../configs/policy.json) remain effective.

W01 proposes a place to retain bounded article-local analyses, actual figures,
QC, discrepancies and scientific critique before an optional Ravel handoff.
It is the first design job in the [W01–W12 roadmap](EVIDENCE_GENERATION_ROADMAP.md).
The [README diagrams](../README.md#intended-workflow) show the wider workflow.

## Review decisions

These choices are adopted as the delegated development baseline, within the
implemented limits in the workspace guide. Approval of design is distinct from implementation acceptance,
scientific contract approval, runtime qualification and permission to dispatch.

| ID | Proposed decision | Consequence and required boundary |
|---|---|---|
| D01 | Permit Weft to retain provisional article-local scientific contracts, code snapshots and evidence | Amend the present Ravel-first ownership rule explicitly before implementing the scientific route. Ravel alone retains canonical questions, accepted methods/evidence and acceptance history; Weft records no canonical acceptance |
| D02 | Use one explicitly configured private evidence root, with immutable case revisions and separate external input roots | No worktree-relative default for live evidence, migration of old runs, or second writable copy. Public Git contains reviewed schemas, reusable code and synthetic examples only |
| D03 | Reuse existing components through versioned scientific integration | Preserve the synthetic packet/executor contract. Add a separately reviewed scientific packet/adapter and ledger integration; never relax fixture validators to admit real data |
| D04 | Keep scientific progress separate from execution state and owner disposition | A failed reproduction may be scientifically informative. An unknown process outcome retains its reservation. Neither AI review nor a successful process creates acceptance |
| D05 | Require a reviewed, allowlisted handoff for any later Ravel integration | A case can end in Weft. Export preparation, integration authority and canonical registration remain separate; no automatic PR, merge or registration |

No current decision is needed about a particular paper, tissue, assay, runtime
provider or scientific threshold. R01's retained reading status and metadata-only
feasibility do not select or authorize a pilot. R02 remains unjudged. The original
frozen 12-paper evaluation remains unchanged and unpassed.

## Ownership and the exact amendment

| Object | Owner when proposal was drafted | Proposed separation; see current implementation scope above |
|---|---|---|
| Discovery identities, source acquisition, reading/B3 proposals | Weft | Weft; reused without rewriting historical records |
| Provisional article-local scientific plan, adapter snapshot and results | Fresh scientific work follows Ravel's contract/runner route | Weft may retain candidate evidence under a distinct namespace and reviewed route |
| Canonical RQ register, accepted contracts/code/results, acceptance history | Ravel | Ravel exclusively |
| Attempt reservation, cancellation and operational receipts | Existing Weft job/launch components within qualified scope | Weft; one authoritative execution ledger and bound provider journal |
| Scientific design choices, interpretation and disposition | Recorded scientist/owner authority | Same; standing approved scope may cover routine choices |

The proposed replacement concept for the broad ownership sentence in
`RAVEL_CONNECTION.md` is: "Ravel owns canonical questions, accepted scientific
contracts/code/evidence and acceptance history. Weft may retain explicitly
provisional article-local plans and evidence under a reviewed workspace contract;
these carry no canonical status and require separate authority for integration."
This distinction is now applied to provisional record storage. Scientific
execution/acceptance authority remains unchanged and gated.

Adoption must reconcile `AGENTS.md`, `RAVEL_CONNECTION.md`, `GATES.md` G3/G4/G8,
`WORKFLOW_AND_STORAGE.md` and the README ownership description in one scoped
change. Preserve scientific constraints; do not treat this document as overriding
them. Runner reuse requires a later compatibility review of Ravel's current
instructions, runner, input contract and output paths. That review has not been
performed here; no Ravel files were modified or scientific scripts invoked.

## Identities and storage

New identifiers are opaque lowercase UUIDs without hyphens, prefixed `ww-`
(workspace), `wa-` (article), `wc-` (case), or `wr-` (run). They are not Ravel
paper IDs, canonical A IDs, DOI-derived filenames, or independent-study counts.
An article references existing catalog/batch/candidate identities and source
versions. Several cases may use one article; one case can cite several sources.
Conflicting article identities remain held until an explicit alias/reconciliation
record resolves them; do not mint a fresh ID to escape an earlier hold.

The proposed configured `evidence_root` is a private absolute local path, supplied
explicitly by the operator. On this machine a possible **new** root is
`X:/GitHub/weft/runs/evidence-workspaces/<workspace-id>/`. This proposal creates
no such directory. Existing `runs/` records stay where they are, referenced read
only. A portable manifest uses logical root names and relative paths, never local
credentials or an absolute machine path. `WEFT_RUN_ROOT` and `WEFT_DATA_ROOT`
remain unimplemented suggestions, not working configuration switches.

```text
<evidence_root>/
  workspace/v000001.json                 immutable workspace identity and bindings
  private-bindings.json                   local root/host bindings; never exported
  control/jobs.sqlite                    one future authoritative execution ledger
  control/launches.sqlite                 bound provider-intent journal, not a rival ledger
  articles/<article-id>/sources/v000001/   immutable source manifest and access evidence
  articles/<article-id>/cases/<case-id>/
    revisions/v000001/case.json           immutable proposed scientific identity
    revisions/v000001/inputs.json         actual input inventory, when available
    revisions/v000001/units.json          W02 unit, pooling and shared-lineage map
    revisions/v000001/feasibility.json    W02 eligibility and inference limits
    revisions/v000001/contract.json       W03 bounded plan, when frozen
    code/<snapshot-sha256>/               pinned authored/adapted code; no secrets
    runs/<run-id>/attempts/<attempt-id>/   append-preserved logs, outputs and receipts
    reviews/<review-id>.json              immutable critiques and actual decisions
    exports/<export-id>/                  new snapshots; manifest written last
  checkpoints/<checkpoint-id>/            verified inactive recovery copies
```

This is a target layout, not a new command interface. Large matrices and full
texts may remain in separate registered read-only roots; input manifests retain
their sizes and hashes. A download/accession listing is not an inspected input.
Access terms, sample metadata and personal notes stay private by default.
No retention guarantee follows from Git ignore rules or a checkpoint receipt.

Filesystem enforcement must resolve roots before access, reject traversal, links,
junctions/reparse escapes and case-insensitive path collisions, and reject overlap
between mutable outputs and inputs, Ravel, historical outputs or another attempt.
Each attempt reserves a fresh directory exclusively before launch. Outputs may be
written during that attempt; sealing its manifest makes those bytes immutable.
Partial output remains retained and labelled incomplete after interruption.
Code from papers is untrusted and can execute only through the isolated adapter.

## Core schema proposal

The review bundle contains a [JSON Schema](proposals/w01/w01-core.schema.json)
and [synthetic example](proposals/w01/example/case.json). The schema covers the
W01 workspace, source-manifest and case-revision envelopes. It uses
`w01-0.1-draft`; every record is `proposal-only`, with dispatch and canonical
acceptance fixed false. It is not loaded by the CLI. An adopted implementation
needs a reviewed schema version and transition validator; this draft cannot be
used as an execution packet. W02/W03 own their detailed payload schemas below.

Common envelope fields are `schema_version`, `kind`, `record_scope`, `created_at`,
`actor`, `dispatch_authorized` and `canonical_acceptance`. Objects reject extra
fields. Actor identity is attributed, not authenticated. Timestamps are timezone
aware but cannot establish prospective design or an unexposed reviewer.

| Record | Exact W01 fields beyond the envelope | Rules |
|---|---|---|
| Workspace | `workspace_id`, `revision`, `previous`, `amendment_reason`, `storage_class`, `execution_ledger_id`, `ownership_review`, `ravel_context` | Private storage only. Initial ledger and review may be null; null conveys no authorization. The optional pinned Ravel context includes repository, commit, lock hash and existing RQ IDs |
| Source manifest | `workspace_id`, `article_id`, `revision`, `previous`, `amendment_reason`, `bibliography`, `origin`, `resources` | Origin binds an existing catalog/batch/candidate and packet hash, or is null for a standalone fixture. Each retained resource has a version, exact locator, access/inspection state and actual file reference when present |
| Case revision | `workspace_id`, `article_id`, `case_id`, `revision`, `previous`, `amendment_reason`, `workspace`, `source_manifest`, `purpose`, `analysis_mode`, `question`, `comparison`, `endpoint`, `inference_scope`, `exposure`, `dependencies`, `holds` | Initial scientific details may be null with a hold. A case is never an execution receipt; W03 must resolve required details before freezing |

A `FileRef` has exactly `{root, path, sha256, bytes}`. The configured root is
`workspace`, `inputs` or `sources`; the path is portable and relative. SHA-256
binds the **exact saved bytes**, including whitespace; no hash of a JSON
reserialization substitutes for it. A record does not contain its own hash.
References, the next revision and ledger events bind its digest externally.
The private root map is not accepted as authority merely because it is supplied
with a copied bundle. Restore uses independently retained expected identities
and hashes, as existing checkpoint/return code already requires.

For initial revisions `previous` and `amendment_reason` are null; later revisions
require the previous immutable file reference and a reason. A write must never
overwrite an existing revision. The transition validator must check same object
identity, contiguous revision, actual predecessor bytes and absence of a fork.
Changed source, units, inputs, comparison, endpoint or code require a new revision
and invalidate affected unstarted work; a display-only correction still retains
history. Exposure and prior outcomes never reset. An extension states why another
comparison is informative and is not an automatic search for a positive finding.

`purpose` uses the existing description, replication, prediction,
perturbation-effect and exploration distinctions. `analysis_mode` separately
records reproduction, adapted analysis or exploration. `exposure` separately
records synthetic fixture, historical replay, exposed exploration or prospective
test, with evidence and limits. Same-data reproduction is not independent
replication, regardless of the name of the purpose or number of publications.

| Referenced payload | Required contents proposed for the owning job | Not supplied by W01 schema validation |
|---|---|---|
| `units` and `feasibility` (W02) | Source citations, accessions and files; sample/library-to-animal/donor/pool map; conditions, timing, denominators, shared lineage and unknowns; inspected status/access terms; resource estimate; eligible/limited/held decision for a specific inference | Truth of metadata, legal access, independent units or data eligibility |
| `inputs` (W02/W03) | Exact file references and roles, input-manifest version, expected formats and binding to units/source | Actual downloaded bytes, QC or scientific sufficiency |
| `contract` (W03) | Purpose, comparison, biological unit, measured endpoint, baseline/controls, intended inference, exposure, reproduction target, justified tolerances/uncertainty, sensitivity plan, stop rules, input/code/environment hashes, resource bounds and recorded scope authority | Approval, freeze, execution readiness or universal thresholds |
| `code` / `environment` (W03/W04) | Immutable snapshot manifest and source commit/dirty-state disclosure; adapter identity; dependency/image lock; input/output mapping; runtime capabilities and enforced limits | Safe execution of author code, compatibility with Ravel runner or qualified worker |
| `ownership_review` (W01 adoption) | Proposal file/schema hashes; D01–D05 disposition; exact reviewed scope, actor/time, retained owner-message locator/hash and conditions | An AI-authored assertion cannot stand in for the owner's decision |
| Attempt receipt (W04/W05) | Workspace/case/revision/run, ledger/job/attempt and launch occurrence/task IDs, packet/contract/input/code/environment hashes, raw runtime observations, start/end/termination evidence, log and output manifest references | A worker's self-report cannot release an unknown attempt |
| QC/critique/disposition (W06/W07) | Bound output hashes and panel/table locators, numerical comparisons and tolerances, discrepancies, sensitivities, issue-linked responses, remaining limitations, reviewer exposure and actual owner decision evidence | Successful software checks, AI agreement or reading preferences are not scientific acceptance |
| Export receipt (W09) | Allowlisted package hash, private-field exclusions, proposed use, reviewed current Ravel base, authorized scope, independent verification and actual merge receipt | Export or PR creation is not integration or canonical registration |

Missing information is explicit null plus a reason/hold, not fabricated IDs,
zero samples, assumed independence or an invented threshold. No pending W02/W03
payload in the example is represented as complete. Semantic validators must check
reference kinds, object identities, file contents, required stage dependencies and
limits; JSON Schema checks only structural shape and selected local invariants.

For this example only, the logical `workspace` root is the example directory.
Its three records bind one synthetic text file with real sizes and hashes; IDs
and timestamps are fictional. It has no database, Ravel context, ownership
decision, scientific input or executed analysis. JSON Schema format checks must
be enabled when validating timezone-aware timestamps.

## Scientific progress and operational state

Scientific state is a **derived projection of bound records**, not an editable
`status` field in `case.json`. The existing execution ledger remains authoritative
for attempts. Proposed scientific event records reference its attempts; they never
grant another execution reservation. The new event tables/schema and their atomic
binding to existing components belong to W05 and are not implemented here.

| Proposed transition | Evidence required before the transition |
|---|---|
| proposed → data-qualified | W02 source/file/unit/lineage assessment and explicit permitted inference; unresolved relevant metadata holds the requested use |
| data-qualified → contract-frozen | W03 immutable contract and inputs/code/environment identities; actual approved design scope and exposure retained |
| contract-frozen → executed | A bound attempt with verified execution and termination evidence; partial/failed execution is shown as such, never as a complete result |
| executed → results-verified | Hash-verified outputs, contract-required QC and numerical checks; missing outputs remain explicit |
| results-verified → scientifically-reviewed | Source/result comparison, discrepancies, sensitivity and issue-linked critique; review may remain unfavorable |
| scientifically-reviewed → disposition-recorded | Actual owner interpretation: retain with limits, revise in a new version, or no further analysis; no forced keep/reject vote |
| disposition-recorded → export-proposed → integrated | Optional W09 package, current-base review and explicit integration authority, then verified merge receipt; canonical acceptance needs its own recorded decision |

Execution additionally requires reviewed ownership, implemented scientific gates,
qualified permitted runtime and authorized scope; the arrow is not a dispatch
command. Reading-only, infeasible, deferred and no-further-analysis dispositions
may end a case earlier with recorded reasons. Operational failure may end with an
incomplete-evidence disposition without inventing missing scientific transitions.

Keep existing operational vocabulary: `queued`, `running`, `cancel_requested`,
`unknown`/`held_unknown`, `failed`, `cancelled` and `local_verified` are component
states with their existing meanings. A timeout, expired lease, cancelled UI turn
or uploaded archive does not prove process termination. Unknown outcomes retain
their slot; the same attempt is reconciled using supported evidence. No new
run/version/ledger can evade that hold. A verified failed or cancelled attempt
permits a new attempt only under separately recorded scope and attempt bounds;
it does not trigger a retry. Recovery copies remain inactive until an explicitly
reviewed ownership transfer; no distributed fencing is claimed.

## Component reuse and changes needed

| Existing code | Reuse | Required later change or limit |
|---|---|---|
| `identity.py`, `discovery.py`, `context.py` | Bibliographic identity, catalog references and pinned Ravel blobs | Bind case/source versions to existing identities; no new canonical register |
| `materials.py`, `reading.py`, `qualification.py` | Inspected-resource bindings, hashes/locators, coverage and separate data/RQ proposals | W02 actual file/unit qualification; existing B3 `review_required` is not eligibility |
| `jobs.py` | Immutable packets, attempt events, reservations and unknown-outcome holds | Scientific packet admission requires a new version and review. Current validator admits only `synthetic-qualification` |
| `executor.py`, `artifacts.py` | Qualification patterns and hash-bound terminal/output evidence | Keep fixture executor intact; W04 needs a separate adapter, output contract and verified isolation. Existing 1 MiB input / 2 MiB archive bounds are synthetic, not scientific capacities |
| `workflow.py`, `launches.py` | Saved-return ingestion, idempotency and provider-intent binding | W05 must connect scientific records without two writers or automatic redispatch; no model/launcher currently supplied |
| `checkpoints.py`, `recovery.py`, `cloud_return.py` | Expected-hash anchoring, inactive restore and same-occurrence evidence | Preserve existing validators/size limits; qualify a separate larger scientific transport if needed. Synthetic return consistency is not scientific verification |
| `review_materials.py`, `quality_review.py`, `review_view.py`, `intake.py` | Source-linked review, retained critic findings and private export patterns | W06/W07 actual numerical outputs and owner dispositions; W09 reviewed scientific export allowlist |

Proposed execution ownership is one workspace ledger, with the existing discovery
catalog and launch journal retaining their different responsibilities. No ledger
is created for each paper/worker. W05 needs crash-consistent intent-before-dispatch
binding and saved-return replay across those stores. W11, separately, must qualify
remote ownership/fencing before any PC-independent operation.

The initial route permits only one explicitly bound active evidence workspace.
Changing its root/ledger is an ownership transfer, never a fresh-start workaround
for unresolved reservations or external holds. Historical ledgers remain preserved
and are not silently adopted by the new coordinator.

## Acceptance checks and delivery boundary

The following are required implementation checks, **not claims of passing tests**.
Use small synthetic files and injected transports; no paper code or cloud task.

| ID | Adversarial fixture | Expected evidence |
|---|---|---|
| F01 | Reject a canonical ID as a case ID; inject acceptance/dispatch flags | Schema/transition rejection; no scientific or Ravel write |
| F02 | Alter a source/input byte, predecessor identity or frozen contract | Bound-reference failure; old revision retained and dependent work held |
| F03 | Request Ravel/historical output path, traversal, junction, collision or existing run directory | Refusal before writes; sentinel input/output files remain byte-identical |
| F04 | Treat pooled libraries/cells/shared accession as independent replicates | Requested replicated inference held; honest descriptive route remains reviewable |
| F05 | Crash before/after reservation, launch acknowledgement or return ingestion | Original intent/attempt recovered once; no duplicate dispatch or competing reservation |
| F06 | Expire lease or lose runtime evidence; try replacement case/ledger or claim cancellation | Unknown attempt still reserves capacity; no relaunch or self-reported release |
| F07 | Return valid outputs with failed numerical checks or unresolved critique | No scientific-state promotion; discrepancies and all attempts retained |
| F08 | Restore/copy the workspace or interrupt export | Restore inactive, partial export incomplete, independently retained hashes required |
| F09 | Export private paths, owner-message bodies, full texts or unapproved fields | Allowlist rejection; dry export makes zero Ravel writes; integration still separate |
| F10 | Supply synthetic packet to science route or science packet to existing executor | Strict version/kind rejection; existing fixture behavior and holds preserved |

W01's initial design delivery was this proposal, core schema and synthetic example.
The subsequent delegated implementation and boundary-fixture results are recorded
in the workspace guide. W04/W05 still require runtime/recovery evidence. The
original structural checks alone do not satisfy F03–F10 or qualify a pilot.

After review, the next bounded implementation is the immutable workspace/reference
validator and ownership boundary fixtures, followed by W02 feasibility schemas and
W03 contracts. W08 real-data execution requires its own reviewed scientific scope
and permitted qualified worker. W10 remains externally blocked on new platform
evidence for the existing occurrence. B4 stays held/excluded, Choi closed, M6
disabled, and Ravel unchanged. No retry, replacement, support message, paid
fallback, deployment, schedule or evaluation-pass claim follows from W01.
