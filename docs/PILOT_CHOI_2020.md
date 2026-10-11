# Pilot P001: Choi 2020, descriptive state recovery

**Status: planned historical end-to-end pilot; not executed by Weft.**
The implementation team has read Ravel's previous outcomes. This is an exposed
regression benchmark, not an unseen discovery test or independent replication.
The software connection check is not completion of this paper pilot.

## Paper and source identity

Choi et al., *Inflammatory Signals Induce AT2 Cell-Derived Damage-Associated
Transient Progenitors that Mediate Alveolar Regeneration*, **Cell Stem Cell**
27:366–382.e7 (2020). DOI [10.1016/j.stem.2020.06.020](https://doi.org/10.1016/j.stem.2020.06.020),
PMID 32750316, PMCID [PMC7487779](https://pmc.ncbi.nlm.nih.gov/articles/PMC7487779/).

The bounded published target is Figure 1B–D: epithelial states and their sampled
composition after injury. The primary computational input is **GSE145031**.
GSE144468 (organoids) and GSE144598 (ATAC) are mapped for context but are outside
the first execution budget. No whole-paper mechanistic reproduction is claimed.

Ravel namespace: `Research Article/gate1_02_choi_2020/`.
Context links: **A0** (conserved transition programmes) and **A1** (distinguishing
transitional states). The pilot measures RNA-state descriptions; it cannot decide
A1's regulatory competence or later functional maturation endpoint.

## Why this pilot

Ravel already has a corrected annotation, preserved failed annotation, explicit
pooling limitation and an unrecovered state. Those make a useful test of whether
an agent reproduces scope and limitations rather than merely generating a plot.
It is small enough to define a single accession and comparison. Selection is
for known evaluation cases, not recency or a claim that it is the most valuable paper.

The pinned Ravel README/plan and corrected D2b record own historical expectations.
Their exact paths and hashes are in the integration lock. The bibliography and
source record identify the primary paper separately from repository observations.

## Current pilot checkpoint

Discovery replay completed and recovered the known DOI; repeating it preserved
paper/RQ candidate identities. Open-access XML was retrieved into an ignored local
reading packet. A [manual, source-bound reading assessment](../records/pilot-reading-20261011.json)
is retained separately from scientific acceptance. The subsequent
[figure, supplement and dataset review](PILOT_CHOI_REVIEW.md) is complete:
all main figures/S1-S7 were inspected, GEO samples mapped and local input integrity
recorded. This does not qualify scientific execution. No worker, frozen new
contract or outcome tolerance has been qualified. Input hashes exist in a review
manifest but are not yet bound to an executable contract. See
[environment recommendation](EXECUTION_ENVIRONMENT.md) and [current state](../PROGRESS.md).

## Scientific contract draft

| Field | Proposed value |
|---|---|
| Work type | Exposed descriptive reproduction and bounded annotation sensitivity |
| Question | Which epithelial RNA-state calls and library composition patterns can be recovered under explicitly recorded QC and annotation rules? |
| Comparison | PBS, day 14 and day 28 AT2-lineage samples; descriptive library summaries |
| Biological/design unit | Two mice per pooled library in source methods; one Tomato-positive GEO library per condition; source mapping reviewed on 11 October 2026 |
| Measured endpoints | QC retention, assigned/unassigned state counts, fractions with explicit denominators, marker support and annotation sensitivity |
| Published target | Figure 1B–D state/composition description; published figure directions are distinct from exact Ravel table regression |
| Principal validity threats | Pooling and no within-condition replication, cell-calling differences, annotation rules, depth and denominator changes |
| Interpretation limit | No animal-level treatment inference, causal lineage claim, repair-function claim or regulatory-competence test |
| Outcome exposure | Known prior Ravel D1/D2/D2b outcomes; any sensitivity pass remains exposed |

Before running, qualify current source files, hashes, runtime and output paths.
Do not replay the old scripts in place: they use historical paths and can overwrite
frozen outputs. Build a new adapter/contract under Ravel governance, retaining old
rules and deviations explicitly. The current JSON is a pilot draft, not an
executable frozen Ravel research contract.

## End-to-end sequence and artifacts

1. **Discovery replay:** execute and record the pilot search from `configs/pilot.json`.
   Record database, query, retrieval time, publication window, pagination and raw
   response hash. The known DOI is an audit target, not evidence of unbiased recall.
   A separate DOI lookup may resolve identity, but must not conceal a missed query hit.
2. **Reading:** verify Figure 1B–D, relevant methods, data availability and relevant
   supplements. Produce a source-located paper card, distinguishing paper findings
   from Ravel's adapted analyses. Access failure holds execution.
3. **Qualification:** resolve GSE/GSM files, lineage selection and pooling; inventory
   matrix dimensions, input sizes and sample joins. Reject animal-level inference
   while allowing the explicitly descriptive branch.
4. **Freeze:** commit the new Ravel contract, adapter, dependency lock, hashes,
   primary annotation rules and output paths. Record exposure and predeclared
   resolution sensitivity (0.3, 0.5, 1.0), without searching for a preferred result.
   Those are Ravel's Leiden settings, not a transcription of the paper's Louvain
   defaults. Preserve prior outcome exposure and freeze the published/adapted
   comparison explicitly; exact author-cell-set recovery is not yet qualified.
5. **Reproduction:** run QC and the bounded state/composition analysis in a new
   output directory. Produce QC/denominator tables, annotation evidence, composition,
   figures, software/resource receipt and a published-versus-adapted discrepancy table.
6. **Extension:** assess how recorded annotation/resolution and depth restrictions
   change the descriptive calls; no donor-level p-values. This is methodological
   robustness, not independent phenotype confirmation.
7. **Interpretation:** distinguish sampled expression states from lineage/function.
   Inspect whether a remaining gap adds anything beyond A0/A1 and existing article
   branches. Record candidate, existing-RQ extension, or no-new-question.
8. **Export:** prepare a Ravel PR with traceable artifacts, current context links,
   the critical hold, discrepancy ledger and updated project state. Do not merge it
   or mint an accepted RQ as part of the pilot.

## Acceptance and deliberate adverse cases

- Identity resolves to the specified DOI; all essential claims have inspected locators.
- Pooling and library-level denominators are retained; an attempted treatment-effect
  inference is held. A hold is an expected successful gate outcome.
- The prior corrected analysis reports four assigned states and no assigned pAT2.
  A fresh result need not be forced to match it; differences require diagnosis,
  not retuning until five states appear.
- Numerical arithmetic replay of a fixed table must reproduce its counts exactly
  and recomputed fractions within a declared serialization tolerance. This is a
  software regression criterion, not biological reproducibility.
- A fresh raw-data rerun needs a justified comparison/tolerance before execution;
  exact environment equivalence is not yet qualified. If unavailable, report an
  adapted/partial reproduction and retain the mismatch.
- No mutations to historical Ravel outputs or unrelated worktrees; verify hashes.
- Negative controls: absent sample identities, altered input hash, a duplicate source
  edition, unreplicated inference and a private-interest field must each stop or
  route correctly before the stage that would misuse them.
- Success requires a complete evidence package, not a positive phenotype or new RQ.

## Resource proposal and next prospective pilot

Revised proposal after the input/host audit: one accession, one worker, up to
4 CPU cores, 6 hours per attempt and 20 GiB of new downloads. Prefer a separate
32 GiB Linux x86-64 host with a 16 GiB worker cap. A local Windows fallback would
instead require a 6 GiB cap and at least 10 GiB available host memory at launch.
All limits remain proposed; [qualification](EXECUTION_ENVIRONMENT.md) must measure
requirements and enforce bounds before analysis.
Existing Ravel data may be referenced read-only after hashes are verified.
Do not silently download raw sequencing reads or expand to additional accessions.

After P001, freeze a search window and eligibility criteria before inspecting
results for a genuinely new paper. That next pilot evaluates live discovery and
generalisation. Reusing this exposed paper cannot establish those properties.
