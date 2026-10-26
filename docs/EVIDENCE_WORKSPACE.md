# Offline article-local evidence workspaces

Implemented on 21 October 2026: private immutable source/case records, data
feasibility consistency checks, frozen plan storage and a fail-closed preflight.
The subsequent [scientific adapter and review implementation](SCIENTIFIC_ADAPTER.md)
adds pinned packages, controlled fixture recovery, numerical plans/critique,
private evidence views and dry handoff proposals. It does not execute author code.
The owner delegated implementation of the W01 proposal and roadmap, with critical
technical or architecture issues returned for attention. This adopts D01–D05 as
the development baseline; it does not claim detailed human technical review,
scientific design approval, a qualified runtime or authority to integrate Ravel.

The [original W01 proposal](W01_WORKSPACE_OWNERSHIP_PROPOSAL.md) and draft schemas
remain design history. Production validators are [evidence.py](../weft/evidence.py)
and [scientific.py](../weft/scientific.py), using `weft-evidence-v1`. The older
`w01-0.1-draft` examples deliberately do not pass production admission. The
[synthetic fixtures](../tests/test_evidence.py) provide complete executable examples
of the original four record types without running their illustrative analysis code.
The adapter guide defines three additional immutable record kinds and their tests.

## Commands and storage

```powershell
python -m weft evidence-init --root X:/WeftEvidence/workspace-v1 --inputs X:/WeftInputs --sources X:/WeftSources --protected-root X:/GitHub/ravel --protected-root X:/WeftHistorical
python -m weft evidence-import --root X:/WeftEvidence/workspace-v1 --record private/source-manifest.json
python -m weft evidence-status --root X:/WeftEvidence/workspace-v1
python -m weft evidence-preflight --root X:/WeftEvidence/workspace-v1 --contract-reference private/contract-reference.json
```

These paths are examples, not created directories. The workspace root must be
explicitly absolute, new, and have an existing parent. Input, source and protected
roots must already exist. Identify the actual Ravel and historical-output roots;
the CLI cannot discover every private protected location on the operator's behalf.
The evidence root must not overlap any of them. Do not put it in public Git.

Initialization creates only `private-bindings.json`, with workspace identity,
host/path binding and external root locations. It creates no execution ledger,
reservation, process, network request, scheduler or scientific job. A local lock
serializes record writes using the existing workflow lock mechanism. This is
cooperative local storage, not protection against an administrator or malicious
code running with the same filesystem privileges.

Records are stored as exact supplied bytes at these derived locations:

```text
articles/<wa-id>/sources/v000001.json
articles/<wa-id>/cases/<wc-id>/case-revision/v000001.json
articles/<wa-id>/cases/<wc-id>/data-feasibility/v000001.json
articles/<wa-id>/cases/<wc-id>/analysis-contract/v000001.json
```

IDs use `ww-`, `wa-` and `wc-` plus 32 lowercase hexadecimal characters. No A ID
is allocated. Workspace IDs are generated at initialization; article/case IDs
are supplied opaque identities, with source origin retained separately. Cross-
catalog alias resolution and biological lineage reconciliation remain reviewed
assertions, not an automatic global identity service.

Each successful import returns a `record` reference with exactly `root`, `path`,
`sha256` and `bytes`. Save this object for downstream imports. Logical roots are
`workspace`, `inputs` and `sources`. Code/environment files can be referenced
under the registered inputs root. Files are checked at each use; paths reject
traversal, symlinks, junction/reparse components, reserved device names, ambiguous
case and hardlinked files. This does not prevent the owner from modifying an
external input later: such changes produce a hold/error and require a new version.

New revisions require the exact predecessor reference, contiguous revision and
an amendment reason. Prior records remain. Changing case exposure mode is rejected;
a later freeze cannot convert exposed work into a prospective test. The current
revision verifies its predecessor chain. Partial writes remain incomplete and
cannot be overwritten by retry; investigate/preserve them before a separately
reviewed recovery. A copied workspace is read-only because its host/path differs.
There is no command to reactivate it or break locks.

## Record fields

All records require exactly the common fields plus their kind-specific fields.
JSON duplicate keys, non-finite values and records exceeding 1 MiB are rejected.
Reference hashes cover exact bytes, not normalized JSON. Source/input size is
checked and streamed for hashing; the JSON-record cap is not a scientific data
capacity or permission to download anything.

Common fields: `schema_version: weft-evidence-v1`, `kind`, `workspace_id`,
`article_id`, `revision`, `previous`, `amendment_reason`, `created_at`, `actor`,
`dispatch_authorized: false`, `canonical_acceptance: false`. Non-source records
also require `case_id`. Initial predecessor/reason are null. Timestamps must have
a timezone. Actor has `id`, `kind` (human/agent/fixture), and
`identity_basis: self-reported`; this is attribution, never authentication.

| Kind | Required additional fields |
|---|---|
| `source-manifest` | `bibliography` with identifiers/title/integrity_status; optional `origin` with catalog/batch/candidate/packet hash; `resources` with resource_id/version/locator/access/inspection/file/limits |
| `case-revision` | `source_manifest` reference; purpose/analysis_mode/question/comparison/endpoint/inference_scope; exposure with mode/note/evidence; explicit `holds` |
| `data-feasibility` | `case` reference; files/units/controls/replication_justification/resources/interpretation_limits/unknowns |
| `analysis-contract` | `case` and `feasibility` references; plan/code_files/environment/outputs/limits/design_review |

Resource access is retained, listed-only or unavailable. Retained resources need
actual byte references. Inspection is not-inspected, metadata-only, caption-only
or inspected; it is the submitter's attestation, not inferred from attached bytes.
Bibliographic integrity is unknown, concern-recorded, review-recorded or
synthetic-fixture. Unknown/unresolved concern holds data qualification.

Case purposes are description, replication, prediction, perturbation-effect or
exploration. Analysis mode separately records reproduction, adapted-analysis or
exploration. Inference scope is unresolved, descriptive, within-sample or
replicated-population. Exposure is synthetic-fixture, historical-replay,
exposed-exploration or prospective-test. Missing comparison/endpoint or unresolved
inference requires explicit holds. All dependencies must name the latest matching
article/case revision. New source versions make dependent unamended cases stale.

Each feasibility file has `file`, `accession`, `sample_ids`, `access_terms` and
`inspection` (metadata-only/inspected). The unit map must cover exactly those
samples. Each unit has `sample_id`, `unit_id`, `unit_kind`, `condition`, `lineage`
and `citations`. Citations contain resource_id/locator/file_sha256 bound to
retained source bytes. Their semantic support still requires actual inspection.
Unknown unit/condition/lineage values are null and cannot be fabricated.

Unit kind is individual, pool, cell, section or unknown. Reused individual IDs
count once per condition. Pooled/cellular/section observations can support bounded
description, but this initial validator cannot qualify replicated-population
inference from them. That restriction is an implementation limit, not a claim
that all replicated pool designs are invalid. Individual replication additionally
needs more than one distinct unit per condition and a design-specific independence/
precision justification; this necessary minimum is not power or validity proof.
Perturbation-effect proposals need documented controls. Resource estimates have
memory_bytes/disk_bytes/wall_seconds; unknown estimates hold qualification.

`eligible`, `limited` and `held` are use-specific **consistency assessments** of
supplied evidence. Eligibility does not certify source truth, sample independence,
scientific validity, access rights or execution permission. Known limitations
must remain in interpretation_limits/unknowns. No prediction or causal model is
fitted by these commands.

A contract plan requires comparison, endpoint, biological_unit, baseline, methods,
reproduction_target, uncertainty, sensitivity, stop_rules and interpretation_limits.
The comparison and endpoint must match its case; feasibility limitations cannot
be dropped. The referenced feasibility must use that same case revision and be
unheld. Code files, environment and supplied design-review evidence are hashed.
The importer does not authenticate a human review or execute these files.

Planned outputs specify path/role/description. Paths must be unique under
`outputs/`; roles are figure/table/qc/log. Limits specify wall_seconds,
memory_bytes, disk_bytes, download_bytes, max_attempts and spend_usd, with spend
fixed zero for this offline route. Bounds below resource estimates are rejected.
Contracts return `contract-recorded`, not scientific readiness or acceptance.
Git freeze, execution isolation, runtime identity, enforced budgets and scientific
review remain required at the future execution boundary.

Status and preflight read without modifying records. Historical revisions are
shown as historical, not silently deleted. Invalid/stale current bindings remain
held. CLI exit 0 means the requested storage/check action completed, 2 means a
hold, and 1 means malformed, tampered or otherwise invalid evidence. An import
of a valid held feasibility record preserves it and returns 2.

## Execution blocker and continuation

Preflight currently **always holds** even if every local binding is consistent.
W04/W05 package preparation and fixture-ledger integration are implemented;
author-code isolation and actual scientific-worker integration are not qualified.
There is no verified permitted runtime bound to a contract, and the scientific
execution policy remains disabled. The synthetic executor's scope is unchanged.

Read-only inspection of the pinned Ravel revision
`bfe26b876221cf6c6fa6f9b16a90cfb516b5998d` confirms that
`analysis/lib/research_governance.py` validates registered owners (lines 110–113),
requires a registered frozen contract and committed code (199–207), and writes
under `analysis/research/runs` (210). Passing a different `--root` does not supply
a compatible registry, scientific schema or isolated worker. No runner was called.
The older local Ravel checkout and its unrelated edits were left unchanged.

The next technical slice is a separately reviewed Weft adapter preserving those
scientific constraints, immutable code identity and execution receipts, with
explicit mappings to the existing job/launch controls. Do not copy the Ravel
runner and remove its registry checks or silently redirect historical outputs.
Its real execution/recovery qualification also needs resolution of the existing
[supported-runtime hold](qualification/NATIVE_RUNTIME_HOLD.md), without repeating
or replacing the held occurrence. No supported runtime-status tool was found in
this local session's catalog; this is not a new probe of the held cloud child.

W01–W03 have an offline implementation baseline. W04/W05 package admission and
fixture recovery, W06 numerical QC, W07 evidence view and W09 dry handoff are now
implemented as documented in the adapter guide. Live author-code isolation,
actual worker integration, W08 real pilot, independent B5 evaluation and
W10–W12 remote/recurring operation remain unqualified. Existing reading views
and synthetic return verifiers retain their narrower responsibilities.

## Verification

Run `python -m unittest discover -s tests -p test_evidence.py -q` and
`python -m weft validate`. The fixture suite covers immutable byte identity,
version/exposure history, stale dependencies, biological-unit accounting,
held feasibility, preserved interpretation limits, output paths, inactive copies,
interrupted writes, hardlinked locks and no-process preflight.
The [validation record](../records/evidence-workspace-validation-20261021.json)
separates targeted checks from the full suite and remaining qualification.
