# Choi pilot: source and dataset review

**Reviewed 11 October 2026. Manual review complete for P001; numerical execution remains held.**
This extends the [initial XML reading](../records/pilot-reading-20261011.json), which
is preserved unchanged. [Review receipts](../records/pilot-review-20261011.json)
and the [input inventory](../records/pilot-inputs-20261011.json) record coverage,
hashes, source editions and limitations. This is an exposed historical benchmark,
not an independent replication or an evaluation of unseen-paper screening accuracy.

## Sources and inspection coverage

- Published [article XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7487779/fullTextXML):
  all main figure captions, relevant results, methods and data availability.
- Author-deposited [manuscript](https://api.repository.cam.ac.uk/server/api/core/bitstreams/cff8fe07-88da-4e51-838e-dc0fd5e05979/content)
  and Figures 1–7: all figure images inspected; Figure 1B–D reviewed in detail.
  Figure TIFF URLs/hashes are in the receipt. These are institutional figure files,
  cross-checked against published captions; main-figure byte equivalence to publisher
  images has not been established.
- [Institutional supplement](https://api.repository.cam.ac.uk/server/api/core/bitstreams/22fd2c5e-5522-4023-a5c0-4a7eda7c05d2/content):
  all seven figure pages visually inspected and all legends read.
  Official Document S1 (`mmc1.pdf`) was recovered as a complete member of the
  [Europe PMC asset response](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7487779/supplementaryFiles),
  with deflate completion, member sizes and CRC32 verified. The archive transfer
  itself timed out and its central directory was not received; it is not recorded
  as a successful complete ZIP download. Official PDF pages 2–17 match institutional
  pages 1–16 exactly in rendered pixels at 110 dpi and normalized extracted text.
  The extra official page is a publisher cover. The initial unaligned comparison
  and the corrected comparison are both retained.
- Fresh GEO SOFT and provider file lists for all three accessions were retrieved.
  GEO/PMC browser challenges and failed binary downloads are retained in the audit.
  Document S2 is article-plus-supplement packaging, not additional study evidence;
  that combined PDF was not retrieved.

Raw PDFs, images, XML and extraction text stay in ignored `runs/` on X:.
Public files contain original assessments, metadata, hashes and source locators.

## Published target: Figure 1B–D

Figure 1A and S1A identify sorted **CD45− CD31− EpCAM+ Tomato+** cells from
SPC-lineage-labelled mice at PBS, day 14 and day 28 after bleomycin injury.
The source methods (`sec4.4.10`) state two mice pooled per experiment. GEO supplies
one Tomato-positive library per condition. The available unit is therefore a
pooled library; individual animals cannot be recovered as independent replicates.

| Published Figure 1B state | Displayed cells |
|---|---:|
| AT2 | 8,524 |
| Primed AT2 | 2,197 |
| Cycling AT2 | 268 |
| DATPs | 836 |
| AT1 | 261 |
| Total | 12,086 |

Figure 1C shows a large AT2 fraction in PBS (97.69%), a lower fraction at day 14
(37.39%) alongside primed AT2 (38.13%) and DATPs (16.83%), and an AT2 fraction of
72.43% at day 28. These are transcribed **plot labels**, not newly computed results.
Fractions must use the retained lineage-positive cells within each library as the
denominator; pooled state counts cannot be substituted for per-library counts.
Embeddings are visualizations, not evidence that the coordinates must match exactly.

Figure 1D and S1B–C distinguish surfactant expression, AT2 identity, inflammatory,
cycling, DATP and AT1 markers. Primed AT2 retains surfactant expression while
showing reduced identity-associated expression and increased inflammatory markers.
Relative-expression plots do not directly specify a threshold on detection fractions.
Figure 1E–F trajectory and S1D enrichment are contextual evidence, outside the
initial B–D execution target. Neither a PAGA edge nor an RNA label establishes fate.

## Figure-to-evidence map

Page numbers below refer to the institutional supplement; add one for official
Document S1. Each row was inspected at the figure/legend level. This is a scope
and design review, not a remeasurement of microscopy, flow gates or reported tests.

| Main figure and supplement | Evidence reviewed | Consequence for P001 |
|---|---|---|
| Fig. 1; S1 pp. 2–3 | Sort, state markers, expression heatmaps, enrichment | Select Tomato-positive input; compare descriptive states and composition |
| Fig. 2; S2 pp. 4–5; S3 pp. 6–7 | Macrophage co-culture, unlabelled profiles, cytokine-treated organoids | Different populations/assays; do not merge their cells into Fig. 1 |
| Fig. 3; S4 pp. 8–10 | SPC/Ndrg1/Krt8 tracing, microscopy and organoid outgrowth | Lineage evidence belongs to those experiments; the RNA pilot does not repeat it |
| Fig. 4; S5 pp. 11–12; S6 pp. 13–14 | Il1r1/Hif1a perturbation, cycling, glycolysis, ECAR and glucose uptake | Expression signatures, metabolic measurements and perturbation effects remain separate endpoints |
| Fig. 5; S7A–B pp. 15–16 | Il1r1-labelled subset and sorting context | Labelled subset and bulk AT2 are not mutually exclusive positive/negative populations |
| Fig. 6; S7A–G pp. 15–16 | ATAC sample comparison, TSS enrichment, peak annotations, loci and motifs | Separate accession; motif/accessibility associations do not establish regulatory competence |
| Fig. 7; S7H–I pp. 15–16 | Early/late AT1 markers, IL-1β withdrawal, 2-DG, human IPF/cancer tissue | Maturation and human observations require their own experiments and units |

Several histology legends define plotted dots as **sections**, with experiments or
mice also reported. Those dots must not be relabelled as independent animals by a
future extraction agent. The Il1r1 comparison includes a haplodeficient control;
do not automatically relabel every control as wild type.

## Dataset mapping and integrity

All three accessions belong to superseries **GSE144553** and the same paper.
Multiple accessions or modalities do not themselves constitute independent replication.

| Accession | GEO samples / processed deposit | Role |
|---|---|---|
| [GSE145031](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE145031) | Six libraries, each with matrix/genes/barcodes; 349,204,480-byte archive | Three Tomato-positive libraries selected; all six mapped |
| [GSE144468](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE144468) | GSM4288824 control and GSM4288825 IL1β organoids; six matrix/TSV members | Context only; no input contents qualified in this review |
| [GSE144598](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE144598) | GSM4291723/24 control and GSM4291725/26 Il1r1-positive AT2; **only two processed bigWigs** in provider archive | Context only; four replicate-specific processed tracks are not available in this deposit |

ATAC methods (`sec4.4.9`) report two independent samples and **five mice pooled
for Il1r1-positive AT2 versus one mouse for bulk AT2 per group**. The deposited
bigWigs cannot be assumed to preserve four independent replicate profiles;
their aggregation must be resolved before a future replicate-level analysis.
Bulk AT2 is the comparison named in the source, not Il1r1-negative AT2.

| Figure 1 input | Condition | Matrix dimensions | Stored entries |
|---|---|---:|---:|
| GSM4304609 / PBS_AT2_Tomato | PBS | 27,998 × 737,280 | 16,264,525 |
| GSM4304611 / Day14_AT2_Tomato | Day 14 | 27,998 × 737,280 | 14,798,870 |
| GSM4304613 / Day28_AT2_Tomato | Day 28 | 27,998 × 737,280 | 15,360,495 |

GSM4304610, GSM4304612 and GSM4304614 are Tomato-negative and excluded. The source
describes that arm as a 2:1 mix of EpCAM+Tomato− and EpCAM− cells, not an interchangeable
control for lineage-positive composition.

**737,280 is the raw barcode universe, not a retained-cell count.** All six files
have the same ordered gene and barcode lists. Gene IDs and barcodes are unique
within those lists; sample identity must be prefixed when libraries are combined.
The three selected compressed triplets total 162,475,103 bytes (about 155 MiB).
Loading their complete dense float32 matrices would require **230.7 GiB** before
overheads; the actual pipeline must process sparse matrices one library at a time.

Verified: archive SHA-256; all 18 member hashes; provider names/sizes; selected
matrix entry-line totals and gzip CRC; all gene/barcode lengths and gzip CRC;
identifier uniqueness; ordered-list hashes. Provider content digests are absent,
so this does not certify remote-byte identity independently of the local archive.
Matrix coordinate/value validity and duplicate coordinates remain loader preflight
checks. No cell calling, biological QC, normalization or clustering ran here.

## Published method and Ravel discrepancy ledger

The published `sec4.4.11–12` describes Cell Ranger 2.0.2, Scanpy 1.3.6, Louvain
clustering, more than 500 and fewer than 7,000 detected genes, and more than 2,000
UMIs. Scrublet uses simulated-doublet ratio 2, 30 neighbors, expected rate 0.1 and
cell score >0.7. Additional Louvain overclustering at resolution 20 and mean
doublet score >0.6, plus marker/UMI review, are described; Scanpy 1.3.4 is also
named in that passage. Exact defaults/seeds and all excluded barcodes are not supplied.

| Issue | Source / pinned Ravel evidence | Required treatment before execution |
|---|---|---|
| Final cell set | Paper: 12,514 captured, 255 contaminants, 12,086 in Fig. 1 | The residual 173 is arithmetic only; do not assert it equals a known doublet set |
| QC differs | Ravel D1: 12,865 pass the paper filter; 11,683 remain after MAD and automatic Scrublet thresholds | Preserve published and adapted filters separately; do not call MAD or automatic cutoffs the published rule |
| Clustering differs | Paper Louvain/old Scanpy versus Ravel Leiden/modern Scanpy | Freeze algorithm, versions, parameters and deviations explicitly; 0.3/0.5/1.0 are Ravel sensitivity settings |
| Annotation differs | D2 had a saturated Sftpc condition affecting AT1/contaminant assignment; D2b preserves it with a correction | Read corrected D2b first, retain D2; do not silently replace expression-based descriptions with detection thresholds |
| Five versus four states | D2b assigns hAT2/cAT2/DATP/AT1 at resolution 1.0, no pAT2 | Missing pAT2 is a result to explain, not permission to tune until five states appear |
| Outcome exposure | Earlier primary resolution was chosen for the most recovered states | A new parameter freeze does not erase that exposure; label all sensitivity comparisons accordingly |
| Reference labels | GEO/methods contain the mixed string `mm9/GRCm38`; ATAC also names GCA_000001635.8 | Preserve the conflict; resolve the actual reference before coordinate-based work or realignment |

Ravel evidence is read from [pinned main](https://github.com/xorca0711/ravel/tree/bfe26b876221cf6c6fa6f9b16a90cfb516b5998d/Research%20Article/gate1_02_choi_2020),
especially `ANALYSIS_TRIAL_PLAN.md` D1/D2/D2b and the corrected D2b run record.
Its historical 11,683-cell QC count and downstream composition denominator must
not be conflated: later annotation can remove additional contaminants.
No historical outputs, claims or worktrees were modified.

## Review disposition

**Proceed to a new contract and worker qualification; keep scientific execution held.**
The review supports a bounded, descriptive **adapted reanalysis** of Figure 1B–D.
Exact published-pipeline replication is not yet supportable without resolving the
original cell set, defaults and manual exclusions. Prefer a primary source-oriented
method specification and a separately identified Ravel-regression comparison;
freeze any departures before execution rather than selecting them after seeing outputs.

The planned adapter must emit staged denominators (raw barcodes → numeric validity
→ basic cell filter → doublet review → contaminants → assigned/unassigned states),
per-library marker evidence, composition and an explicit discrepancy table.
No animal-level p-values, causal fate conclusions, accepted A0/A1 claim, new RQ or
automatic export follows from this review. Worker recommendation and the remaining
release conditions are in [Execution environment](EXECUTION_ENVIRONMENT.md).
