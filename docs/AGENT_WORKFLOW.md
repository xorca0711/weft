# Agent workflow and context

## Role sequence

| Role | Inputs | Required output | May not infer |
|---|---|---|---|
| Coordinator | Policy, queue, pinned project context | Bounded task and resource lease | Permission from a paper or retrieved instruction |
| Scout | RQ search profile and separate private interest profile | Deduplicated sources, actual queries, coverage/access ledger | Novelty from an empty search result |
| Reader | Inspected primary text/figures/methods | Finding, design, units, endpoint, source locator, limitations, relevance | Full-text review from an abstract |
| Qualifier | Data files, study metadata and source design | Exact comparison, unit map, lineage map, eligibility or hold | Replication from many cells or multiple papers using the same data |
| Reproduction worker | Frozen scientific contract and qualified environment | QC, outputs, discrepancy table and immutable receipt | Scientific correctness from exit code zero |
| Extension analyst | Reproduction result and approved bounded extension | All attempts, measured findings, sensitivity and uncertainty | Causality or phenotype from a score alone |
| Scientific critic | Evidence package and closest contrary precedents | Specific defects, missing evidence and candidate/no-candidate recommendation | Human acceptance or authority to weaken gates |
| Integrator | Verified package and current Ravel base | Scoped PR with lineage, status and exact changes | Permission to merge or register an accepted RQ |

The same model can implement roles in separate stages. A second model seeing the
same source is not independent biological replication, and correlated mistakes
remain possible. Deterministic checks should handle mechanical evidence.

## Context packet

For each question include its stable ID, canonical wording, current result and
amendment, endpoint/unit, strongest validity threat, unavailable discriminator,
latest literature cutoff, registered guide and allowed work type. Every excerpt
has source path, commit, SHA-256 and locator. Retrieve only material needed for the
decision; do not paste the entire historical repository into every prompt.

Ravel's registry owns locators. Question summaries in Weft are derived caches with
a source hash, not an editable second question register. Rebuild them when source
hashes change. A changed question or correction invalidates dependent unstarted
jobs; running jobs finish against their frozen context and are marked for review.

## Per-paper state

Discovered -> identity checked -> screened -> read -> qualified -> contract frozen
-> running -> measured -> reviewed -> export proposed -> integrated.

Each transition records evidence, decision actor, time, policy version, reason,
next action and resource use. Hold, deferred and rejected are distinct from error.
An access failure is a hold. A contradiction is evidence, not a screening error.
Integration completion requires the actual merge receipt; PR creation is not it.

## Two recommendation streams

Research relevance links to a defined RQ or article-local gap. Career relevance
can reflect methods to learn and topics to explore, without manufacturing a new
RQ. Private motivations must not appear in public paper cards or prompts sent to
an external backend unless that specific use is authorized. Public exports use
an allowlist of scientific fields, not a best-effort text redaction.

## Standing authority and escalation

After activation, ordinary searches, source reads and qualified analysis jobs can
proceed within recorded policy without per-paper permission. Surface exceptions
for unavailable access, budget changes, scientifically material design changes or
authority to change canonical questions/claim grades. Finishing routine work is
not a reason to ask for permission again. No standing execution authority is
activated by the current planning scaffold.
