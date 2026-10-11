# Evaluation and release criteria

## Separate what is being evaluated

1. Retrieval: did the search find relevant direct, contrary and adjacent work?
2. Screening: does the ordering save reading time without systematically hiding work?
3. Extraction: are designs, units, endpoints and conclusions supported by sources?
4. Execution: do hashes, environments, QC, computation and discrepancy reports hold?
5. Interpretation: are limitations, negative results and candidate questions justified?

## Pilot evaluation

P001 is an exposed historical benchmark. Its reference set includes successful,
partial and unavailable comparisons from Ravel. Record fidelity and correct holds;
do not report discovery accuracy or biological novelty from it. The current offline
unit tests verify only the scaffold and read-only manifest connection.

## Prospective discovery evaluation

For M6, assemble a reviewed pool through broader searches independent of the model's
shortlist. Freeze relevance criteria and the publication/indexing window. Include
preferred and nonpreferred journals, contradictions, unfamiliar terminology and
adjacent tissues. Record reviewer disagreement; an unresolved label stays uncertain.

Report retrieval recall within that bounded reviewed pool, precision at a fixed
reading budget, missed-paper rate in randomly audited low-ranked records, source-
support errors, incorrect eligibility decisions, human reading/review time and
observed model/compute/storage cost. State denominators and uncertainty. Neither
that pool nor absence of observed misses proves exhaustive literature coverage.

Evaluate versions and source cohorts together to avoid train/test leakage. Repeat
against future publication windows and at least one additional paper family before
expanding scope. Do not tune and report on the same evaluated examples as if unseen.

## Acceptance policy

Critical errors (invented sources, false independent units, unsupported causal
claims, overwritten evidence, private-data export or unauthorized execution) block
release until resolved. Aggregate discovery/extraction targets and review capacity
must be agreed before the prospective evaluation; no unsupported universal accuracy
percentage is supplied here. Publish both performance and unresolved exceptions.

## Feedback without narrowing the field

Keep a random audit stream and a deliberate contradictory/adjacent stream. Do not
train relevance only on clicks or accepted positive findings. Journal priority and
career relevance are distinct from source support. Keep model/prompt/policy versions
with each label and reassess drift after changes. Multi-agent agreement does not
substitute for source-grounded evaluation.
