# Phase 4: scientific-quality review

**Status: critic-assisted development review and multi-source adjudication imports
implemented; independent scientific-quality qualification remains pending.** The owner will be
the primary human reviewer and requested a separate critic AI before that review.
The critic is not a human reference. Its agreement with Weft is not an accuracy
estimate. The assisted route is separate from the existing independent B5 scorer.

## What was reviewed on 20 October 2026

A separate critic inspected the evaluation contract, code and public evidence,
then checked primary article pages for two previously screened, non-B4 papers.
It saw the historical outcomes. Root checked the condensed findings against two
newly retained Europe PMC metadata/abstract snapshots: one exact DOI request per
paper, no live catalog writes or source-material downloads.

| Development case | Historical decision, unchanged | Review boundary |
|---|---|---|
| [Lung hydrogel paper](https://pubmed.ncbi.nlm.nih.gov/42786734/) — `10.1002/adhm.71751` | A0 hold; A1 hold | Abstract supports lung context; units, controls, causal support, data usability and current RQ compatibility remain unresolved |
| [Periodontal hydrogel paper](https://pubmed.ncbi.nlm.nih.gov/42768922/) — `10.1002/adma.75042` | A0 reject; A1 reject | Dental alveolar tissue/endpoint mismatch with the supplied pulmonary context; no judgment of general study quality |

These are **two paper/context cases**, representing four historical links. They
were purposively chosen after exposure. They are not separately frozen A0/A1
compatibility reviews, an unseen sample, a reference bibliography or an estimate
of retrieval accuracy. Current Ravel dossiers were not read. The remaining 71
deferred non-B4 papers were not reviewed. Relevant positives, independently
identified contrary evidence and source-complete B3 cases remain missing.

The critic's publisher-only observation about the dental paper's data-availability
statement was not promoted into a metadata-bound finding. Its source was not in
the retained abstract snapshot. Figure pixels, supplements, dataset files,
independent units and cross-paper lineage remain uninspected/unverified. Absence
from an abstract is missing evidence, not proof of a study defect or data absence.

The private handoff is in ignored
`runs/phase4-review-20261020/human-handoff/`. It contains the exact packet and
metadata bytes, readable review cards, a blank human response template, accounting
and a hash manifest. No human answer, identity attestation, acceptance threshold
or scientific decision was filled in by an agent. The public
[checkpoint](../records/phase4-development-review-20261020.json) contains only
bounded provenance and status, not the unrestricted source snapshots.

## Critic-first adjudication workflow

```powershell
python -m weft quality-review-export --packet private/review/packet.json --output private/handoff-001
python -m weft quality-review-export --packet private/review/packet.json --adjudication private/human-response.json --output private/handoff-002
```

Use new output directories. The exporter reads local JSON snapshots only. It
verifies exact DOI identity, hashes and JSON-pointer locators before producing a
private immutable package. Source paths remain portable, with collisions against
generated files rejected. Original critic findings and subsequent human answers
are retained separately and shown together. An interrupted export has no final
manifest. No live record or held disposition is changed.

The human records separate reading, data-use and context/RQ judgments using the
existing label vocabulary, plus agreement, disagreement or uncertainty on critic
findings. Reasons and source locators are required for known judgments. Null
labels and uncertain findings remain unresolved; a human disagreement records
the adjudicator's decision rather than critic–human consensus. Anyone may leave
an item unknown instead of stretching beyond their expertise or available evidence.

The mode is fixed to `ai_assisted_adjudication`, with
`independent_reference=false`, `blind_to_agent=false` and exposure recorded.
It supports synthetic or development cases only. It produces no independent
quality metric, pass threshold or scientific authority. Actor identity is an
attestation. A hash and a valid locator establish retained source identity, not
that a claim is scientifically supported. The module invokes no model; the
externally supplied critique is explicitly AI-authored.

Schema v1 retains its exact single-record Europe PMC metadata contract. Schema v2
adds separately hashed full texts, derived text, figures, supplements, original
review records, human authority and acquisition receipts. It retains source
versions, declared inspection scope and derivation parents. The exporter performs
no source retrieval or scientific inspection. Do not cite a supplement, figure,
dataset or current RQ dossier using the abstract's hash. See the
[full-text/transfer guide and remaining qualification stages](PHASE4_FOLLOW_THROUGH.md).

## Scientific rubric and unresolved requirements

| Review question | Evidence the reviewer needs | What must not be inferred |
|---|---|---|
| Does the cited passage support the specific statement? | Exact claim, source version, locator and inspected scope | A valid hash is not entailment; author mechanistic language is not verified mechanism |
| What comparison and endpoint were measured? | Methods, relevant figure/result and purpose of the proposed use | Repair morphology, a score or expression change is not automatically lineage/function/mediation |
| What is independently replicated? | Animal/donor identifiers, pooling and sample-to-assay mapping | Cells, sections, technical repeats and publications are not automatically independent units |
| Are the controls adequate for this inference? | Actual comparator and design, matched to the intended claim | Neither a universal extra-control requirement nor causal acceptance from association |
| Are data usable and independent of other evidence? | File/accession inventory, access, unit mapping, shared cohorts/source lineage | Author-request availability is not verified access; reused data is not replication |
| Are holds appropriate and retrieval omissions visible? | Missing-material record, rejected/deferred/contrary cases and external bibliography | Missingness is not rejection; favorable selected cases are not a recall denominator |

Before independent qualification, retain a concrete owner-reviewed sample and
acceptance criteria, reference-reviewer authority, sampling/coverage rationale,
per-item exposure, evidence versions and a genuinely independent comparison
bibliography. Keep the original predictions and reference judgments immutable;
new adjudications do not overwrite or redate historical outcomes. Freeze those
decisions before evaluating new outcomes. No sample size or threshold has been
invented here.

The existing [B5 contract](B5_EVALUATION_PREPARATION.md) remains strict. Assisted
records cannot be passed directly into its independent-reference schema. The
critic found that an explicitly unblinded reference could previously enter the
`declared_unseen` stratum when exposure fields said `none`; the scorer now
conservatively classifies such records as exposed. This corrects accounting and
does not relax independence or scientific-admission requirements.

The critic also found and the implementation corrected two handoff defects:
portable source paths and visibility of human corrections. Tests cover those
boundaries, falsified reference-mode flags, source/locator tampering, missing and
disputed answers, partial export and the exposure correction. Software test
results are not scientific evaluation results.

B4 `10.1002/advs.77773` / `PMC13634473` is excluded entirely. Its source hold is
not retried or rerouted. Choi remains closed, M6 disabled, platform launch access
unqualified and Ravel unchanged. This local development review does not qualify
the held live B4/B5 route or authorize recurrence.
