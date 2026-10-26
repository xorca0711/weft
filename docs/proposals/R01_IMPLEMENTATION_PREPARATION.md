# R01 implementation preparation

25 October 2026. Supports [R01-D01](R01_PILOT_CONTRACT_20261021.md); no real analysis,
frozen scientific contract, acceptance margin or owner approval is created.

## Implemented calculation boundary

[r01_analysis.py](../../weft/r01_analysis.py) accepts frozen population expression
vectors. Each binds a deposited pool, population, representation, recipe hash,
cell-membership hash, observed cell count, ordered unique genes and finite values.
The comparison is uninjured GSM9136218 versus D40 GSM9136222. It rejects feature/
recipe mismatches, invented sample IDs and invalid denominators. It does not infer
annotations, select genes, transform an assay or average cells for the author.

Pearson correlation uses scaled, centered vectors; constant profiles remain
unavailable. Processing sensitivity requires identical genes, cell membership and
denominators across representations. Reports retain both recipes and pools. No
biological CI, condition significance, causal/lineage claim or published
reproduction pass is computed. Fixing membership does not resolve original
selection bias. Analytic tests cover positive/negative/zero correlation, large
finite values, constant vectors, alignment, invalid values and membership drift.
Real vectors must be produced under a frozen recipe on the qualified worker.

## Source Data inspection

Fetched the publisher's [Source Data workbook](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-026-72331-w/MediaObjects/41467_2026_72331_MOESM11_ESM.xlsx)
under a 16 MiB cap: 9,965,527 bytes, SHA-256
`e74d84dea486e151c31c55ecdab34533d34e597d366289cace5e79c533601adc`.
ZIP expansion was bounded at 64 MiB; declared uncompressed contents total
10,060,750 bytes. Read workbook/sheet XML and cells without evaluating formulas,
following external links or running code. Private source bytes and cell-located
inspection are retained under `runs/r01-source-preparation-20261025/`, outside Git.

Six sheets: `Figure 2 ` (A1:AA23), `Figure 3` (A1:AB10), `Figure 5` (A1:O63),
`Figure 6` (A2:AE33), `Fig. S3` (A2:T22), `Fig.S10` (A2:U53). No Fig. 1 worksheet
or inspected cell table supplied the needed Fig. 1l targets or cell labels.
Embedded images were not inspected; this is not a claim about every attachment
or unpublished author resource. The previously inspected three 50-gene lists
cannot substitute for cell membership or the whole-transcriptome recipe.

## Remaining freeze work

| Required item | Evidence / next action |
|---|---|
| Counts, features, barcodes and resource estimate | GEO identities/metadata retained; inspect actual matrices within the qualified route |
| Cell membership / annotation | Recover source labels, or prepare a reviewed amendment for independent descriptive annotation |
| Assay, transform, aggregation, common features | Missing details cannot be replaced with guessed Seurat defaults |
| Numerical targets / tolerance | Not inferred from the approximate article range; reproduction remains held |
| Environment | Reported R 4.2.2, Seurat 4.2.1, Cell Ranger 4.0.0 and mm10 are provenance, not a lock; need transitive versions/hashes, image/platform digest and acquisition budget |
| Real output QC | Preserve every cell/gene/pool denominator, recipe, attempted variant and discrepancy |
| Scientific disposition | Review completed descriptive scope and limits; routine source audits remain delegated to AI |

The remaining analysis implementation depends on these recipe choices. A different
plausible analysis must be labelled and reviewed before replacing reproduction.
No twelve-paper manual claim-audit task is reinstated.

## Evidence-generation evaluation proposal

Keep the original frozen reading evaluation unpassed. R01 remains exposed
exploration with a historical reproduction component. A new evaluation should
record whether the comparison was answerable, lineage complete, all attempts
retained, numerical checks passed, discrepancies explained and interpretation
bounded by pooled descriptive evidence. An unfavorable or unresolved result may
meet honest operational reporting criteria. A schema/run pass cannot establish
scientific usefulness or general accuracy. Freeze appropriate criteria/references
and obtain consequential owner disposition separately before claiming qualification.
