# B5 evaluation preparation

Status: offline evaluation tooling implemented and tested with synthetic inputs;
independent fresh-paper evaluation has not run. No quality claim is established.
The exposed Choi pilot, current development candidates and B4 interrupted material
cannot be relabelled as unseen. B4 remains held; this plan does not reroute it.

The owner-requested [phase-4 critic-first handoff](PHASE4_SCIENTIFIC_QUALITY_REVIEW.md)
is a separate exposed development mode. Its AI-assisted human adjudications are
not independent B5 reference labels. The independent contract below is unchanged;
unblinded references are now excluded from the `declared_unseen` stratum.

Before an independent batch, retain a versioned evaluation plan covering:

| Decision to freeze | Required record |
|---|---|
| Sampling | Search dates/queries, eligible universe, independent selection method and actual inclusion probabilities when estimable |
| Coverage | Relevant, contrary, adjacent, low-ranked/rejected and ineligible papers; journal prestige cannot be the relevance label |
| Exposure | Per-paper prior access by the agent and evaluator; distinguish unseen from exposed material |
| Reference labels | Independent human labels and evidence locators for reading priority, data usability and RQ compatibility separately |
| Disagreement | Preserve agent and human judgments, uncertainty and adjudication; never overwrite the original label |
| Retrieval omissions | Independently assembled comparison bibliography with its coverage limits; a search return alone is not a recall denominator |
| Outcomes | Reading-decision errors, unsupported citations, false readiness, missed relevant/contrary papers and appropriate holds, each with its denominator |
| Operational outcomes | Duplicate dispatches, unknown submissions, recovery success, resource/time usage and failed/held attempts |
| Thresholds | Owner-reviewed sample size and acceptance criteria before outcomes; no invented margin or post-hoc pass threshold |

The author of the screening response should not create their own supposedly
independent reference labels. Human review can be blinded to the agent decision
where feasible; record departures. Material-access restrictions require explicit
missingness/holds, not automatic negative relevance labels.

## Offline accounting interface

`weft/evaluation.py` validates a frozen, externally reviewed plan and computes
separate reading-priority, data-use and RQ-compatibility metrics from supplied
agent and independent human judgments. The [completion review](ROADMAP_COMPLETION_REVIEW_20261013.md)
documents `evaluation-plan` and `evaluation-score`; synthetic schema examples
are in `tests/test_evaluation.py`. The caller must retain the canonical JSON plan
hash before outcomes, and the CLI rejects a different hash before reading judgments.

Missing records/labels and disputed references remain unresolved. Metrics include
their denominators, confusion matrices, unsupported positives relative to the
supplied reference, exposure strata and unblinded-reference counts. The unit is
a frozen item/packet, not an independent paper or study. Repeated papers/lineages
are not de-duplicated into an independence claim. Citation hashes establish source
identity, not semantic support. Actor identity, owner review, blinding, independence
and timestamps are attestations. No model is called and no threshold, scientific
admission, release qualification or dispatch permission is inferred.

Next: agree the independent sample and reviewer only when the supported launcher
and review access are qualified. M6 cadence, scope and usage ceilings remain a
later owner decision. These requirements complement, rather than replace, the
[B1–B5 roadmap](DISCOVERY_SCREENING_BACKEND.md).
