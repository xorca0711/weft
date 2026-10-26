# Automated gate specification

**Status: scientific gate engine still proposed.** Manual metadata retrieval,
identity holds, reading-priority transitions and source-hash/locator checks are
implemented. [B3 evidence records](EVIDENCE_QUALIFICATION.md) add coverage and
use-specific proposal consistency checks. Semantic claim review and G3–G8
runtime transitions are not. Ravel's existing
gate remains the execution authority for Ravel analysis.

The [offline evidence workspace](EVIDENCE_WORKSPACE.md) adds immutable record,
file/unit consistency and frozen-plan checks. These are preparation for G3/G4,
not implemented scientific acceptance transitions. Every scientific preflight
currently holds; source truth, review authority and runtime enforcement are not
established by those record checks.

The [batch interface](BATCH_SCREENING.md) enforces bounded discovery, current-source
response ingestion and attempted XML-read limits. It does not implement the full
gate engine below. Agent reasons and actor identities are not semantically or
cryptographically certified; reading priority is never scientific eligibility.

Every gate returns `pass`, `hold`, `reject` or `error`, with a reason code, inspected
evidence references, policy/version, actor, timestamp and next action. Unknown is
never silently treated as true. A hold has a reopening condition. A reject remains
searchable with its rationale; ranking alone does not delete a paper.

| Gate | Evidence required | Automatic decision/hold | Authority |
|---|---|---|---|
| G0 Scope/resources | Versioned policy, permitted source, available hard caps | Hold undefined or exhausted resources; career-only items do not launch compute | Operational policy |
| G1 Identity/access | DOI/PMID or stable ID, edition, correction/retraction state, retrieval/access record | Resolve strong bibliographic IDs; retain edition relationships without counting independent studies; unresolved identity or inaccessible needed content holds the affected stage | Mechanical checks plus source assessment |
| G2 Reading relevance | RQ link or career reason, actual source locators, inspected-text scope | Queue direct, contrary and adjacent findings separately; abstract-only screening cannot authorize execution | Model proposes; sampled evaluation checks quality |
| G3 Data eligibility | Accession/file identities, unit/condition map, pooling, controls, endpoints, source lineage | Fail requested population inference without identifiable independent units; allow bounded description under its own contract | Ravel scientific rules |
| G4 Execution readiness | Frozen committed contract, input/code hashes, isolated worker, environment lock, output isolation, budget | Hold missing hashes/runtime; reject writes into frozen output paths; no undeclared shell action from source text | Runtime enforcement and Ravel runner |
| G5 Reproduction | Specified source target, comparable methods, QC, output receipt and discrepancy ledger | Classify exact/adapted/partial/unavailable reproduction; a completed script alone cannot pass scientific fidelity | Predeclared comparison, reviewer where needed |
| G6 Extension validity | Bounded purpose, contrasts, exposure, unit, uncertainty and attempt ledger | Preserve nulls; hold invalid inference; do not tune until positive; new choices need amendments | Scientific contract |
| G7 Question contribution | Published finding -> observed result -> unresolved contrast -> informative next test; recent/older/contrary precedents | Produce article-local candidate, evidence update or no-candidate disposition; no mandatory new RQ | Proposal only |
| G8 Integration | Current Ravel base, artifact hashes, allowed public fields, required checks, review status | Prepare scoped PR; stop on conflicts/stale context; no automatic merge or accepted-claim promotion | Recorded owner/repository authority |

## Required failure controls

- Reused dataset or preprint + article must not increase independent-study count.
- One pooled library per condition cannot pass a replicated treatment-effect gate.
- A paper outside preferred journals must remain discoverable in broad/contrary
  searches. Priority is an attention setting, not evidence of validity.
- New correction or source version invalidates unstarted dependent decisions.
- A changed file after freezing must fail hash verification; no silent update.
- Receipt verification failure prevents synthesis/export even if plots exist.
- No early canonical RQ ID, personal-context export, or execution outside budget.
- Low-ranked and rejected papers remain available for missed-paper audits.

## Scientific thresholds

Do not put universal biological effect sizes, donor counts or p-value cutoffs in
repository-wide policy. The study contract justifies its precision, endpoints,
multiple-testing family and comparison-specific validity. A missing justification
restricts inference. Observed exploration remains exposed after later freezing.

## Enforcement development

M3 must implement explicit state transitions and immutable evidence references,
then test missing/tampered/stale evidence, every legal/illegal transition, retry
idempotency and crash recovery. M4 supplies measured QC and scientific checks.
Passing a record schema cannot establish that a quoted source supports a claim.
Policy or gate changes are separately reviewable and must not retroactively make
a failed run pass.
