# R01 pilot contract for review

Draft R01-D01, 21 October 2026. **Held; not a frozen executable contract.**
The [25 October implementation preparation](R01_IMPLEMENTATION_PREPARATION.md)
adds tested correlation/sensitivity mechanics and the bounded Source Data
inspection. It does not supply the missing Fig. 1l recipe or freeze this draft.
Recommended first pilot: descriptive reproduction of the paper's transcriptomic
comparison, followed by a bounded check of its sensitivity to processing choices.
R01 remains an article candidate/cross-tissue reference. No canonical RQ or A ID,
Ravel acceptance, prospective label or owner scientific approval is created.

## Question and deliverable

How robust is the reported resemblance of day-40 regenerated epithelial
populations to uninjured limbal populations when the deposited data are processed
using the reported workflow and compared with an unintegrated expression analysis?

The main comparison is D40 versus uninjured control within explicitly documented
qLSC/aLSC and corneal epithelial population definitions. D2, D5 and D10 provide
descriptive temporal context. The target is Fig. 1l, with Fig. 1g–h as clustering/
annotation context and Fig. 1j–k as a secondary expression-profile check if the
underlying gene lists and definitions can be recovered. No automatic successful
reproduction verdict is possible until the original per-comparison values, feature set, transform
and numerical tolerance have a documented basis.

The Results text reports approximately 0.85–0.90 resemblance for baseline CE/LSC
comparisons and 0.99–0.995 at D40, but this range is not a per-panel numerical
target or an acceptance margin. It also selects candidate regenerating cells by
their clustering with native LSCs. Preserve and critique that selection rule:
conditioning on transcriptomic similarity can affect the similarity subsequently
reported. Holding membership fixed across representations tests processing
sensitivity; it does not independently validate the selection or lineage claim.

## Bound source and design facts

Article: *Aged differentiated cells reverse into native stemness-like state by
niche cytokines to sustain lifelong homeostasis and tissue repair*,
[DOI 10.1038/s41467-026-72331-w](https://doi.org/10.1038/s41467-026-72331-w).
The retained R01 XML was inspected directly: 212,661 bytes,
SHA-256 `f3b297a6f9ee2f932daae83286c897a98b7a7d175ca96d9ea139052bd22cfe0e`.
Locators: Methods → “Tissue collection and single-cell preparation”, Methods →
“Single-cell RNA-seq data analysis”, XML `fig[@id='Fig1']`, and Data availability.

Fresh metadata-only reads of [GSE303805](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE303805)
and its five GSM records on 21 October confirm the mapping below. Each is labelled
`rep1` and `Batch 1`; each deposits a raw matrix, feature table and barcode table.
The retained Methods report four eyes pooled per condition from 4-month-old
K15-GFP mice. Eye-to-animal identities and independence across conditions are
unresolved. Fig. 1 also describes 2-month-old imaging cohorts; those cannot be
silently assigned to the sequencing samples.

| Deposited sample | Condition | Biological unit used for this pilot |
|---|---|---|
| GSM9136218 / S1 | Uninjured control | Deposited pooled-eye sample; individual animals unresolved |
| GSM9136219 / S2 | Day 2 injury | Deposited pooled-eye sample; individual animals unresolved |
| GSM9136220 / S3 | Day 5 injury | Deposited pooled-eye sample; individual animals unresolved |
| GSM9136221 / S4 | Day 10 injury | Deposited pooled-eye sample; individual animals unresolved |
| GSM9136222 / S5 | Day 40 injury | Deposited pooled-eye sample; individual animals unresolved |

Five deposited samples do not provide five replicates of either condition. Cells
are observations nested in a pool, not independent biological replicates. Pool
labels will use the GSM accessions; they will not be presented as donor IDs.
Cell counts, retained denominators and matrix dimensions remain uninspected.

The [GEO file list](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE303nnn/GSE303805/suppl/filelist.txt)
lists 15 compressed component files and a 594,298,880-byte archive. Size and names
do not establish cell calling, annotation, validity or uncompressed resource use.
Seven small GEO metadata files and the 13,886-byte Supplementary Data 1 workbook
were retained. Direct worksheet inspection resolved three lists of 50 distinct
genes each on `Sheet1`: qLSC at A2:A51 (labels B2:B51), aLSC at D2:D51 (labels
E2:E51), and CE at G2:G51 (labels H2:H51). All corresponding cluster labels match.
This resolves the reported signature lists, not per-cell labels or the Fig. 1l recipe.
The publisher Source Data workbook retrieval exceeded the separate 8 MiB source
inspection bound and was stopped without retaining a partial workbook. No matrix,
archive, author repository or author code was downloaded/executed. Source bytes
and URLs are hashed in the private metadata manifest; the public validation record
retains their hashes without copying the article full text.

## Proposed methods to freeze after inspection

1. **Feasibility first.** On the qualified preparation route, retrieve the 15
   listed components once, hash compressed bytes, inspect dimensions and sparse
   format, match feature/barcode axes, and retain per-sample inventory/QC. Bound
   decompression and reject unsafe archive entries if an archive route is used.
   Do not densify the count matrix. Determine raw-droplet versus filtered-cell
   status, cell-calling provenance, feature types, mitochondrial gene definition,
   ambient RNA/doublet handling and available annotations before comparison.
2. **Reported baseline.** Methods report R 4.2.2, Seurat 4.2.1, Cell Ranger 4.0.0/mm10,
   SCTransform and anchor integration, PCA/UMAP, SNN resolution 0.5. Reported
   exclusions are detected genes below 200 or above 5,500, mitochondrial percentage
   above 15%, or UMI count above 70,000. The paper introduces these as examples;
   they are source-backed baseline candidates, not proof of a complete code recipe.
   Pin package dependencies, reference build and relevant parameters before use.
3. **Annotation and endpoint.** Preserve the inspected Supplementary Data 1 gene
   lists without selecting a more favorable subset. Recover author cell labels and Fig. 1l
   correlation inputs if available. For reproduction, retain the exact averaging,
   transform and feature recipe. For the proposed sensitivity analysis, freeze a
   common gene set and population labels, then compare expression correlations
   from integrated and unintegrated representations without selecting genes to
   maximize agreement. If author labels/recipe are unavailable, hold reproduction;
   a new annotation analysis needs a labelled amendment and reviewed marker basis.
4. **Sensitivity.** Keep the reported QC baseline and compare integrated versus
   unintegrated expression with cell membership held fixed. Record annotation
   ambiguity explicitly. Additional QC cutoff or label variants require justified
   values frozen after input inspection; do not search thresholds until a desired
   resemblance appears. No cell-level condition p-value becomes population evidence.
5. **Uncertainty and interpretation.** Report per-pool descriptive estimates and
   cell/gene denominators with all processing variants. Biological confidence
   intervals and condition-effect significance are not estimable from these
   deposited pools alone. Do not infer lineage conversion, fate, function, cytokine
   mediation, generalization to lung or causal mechanism from this transcriptomic
   pilot. Other assays in the paper are not rerun or inherited as pilot evidence.

The article and results have already been read. Record exposure as
`exposed-exploration`; identify the reproduction component as historical replay.
The pilot cannot be called a blinded or prospective test.

## Outputs and finite operating envelope

| Planned output | Content |
|---|---|
| `outputs/input_inventory.json` | Exact input hashes, shapes, feature types, sample/pool map and unresolved metadata |
| `outputs/qc_by_sample.csv` | Cells/barcodes before and after every filter, reasons, denominators and processing versions |
| `outputs/annotation_review.csv` | Frozen labels/marker provenance and ambiguous populations |
| `outputs/correlation_table.csv` | Fixed comparison, gene/cell counts, per-pool values and processing variant |
| `outputs/reproduction.png` | Published-target comparison only when its numerical/annotation basis is available |
| `outputs/sensitivity.png` | Integrated/unintegrated comparison with explicit retained membership |
| `outputs/metrics.json` | Adapter-compatible scalar checks; no invented target/tolerance or biological CI |
| `outputs/discrepancies.json` | Missing recipe/targets, nulls, mismatches and unresolved critiques |
| `outputs/run.log` | Code/image/package hashes, attempted stages, warnings, failures and resource observations |

Proposed ceiling for one supervised pilot: **one attempt, 2 hours, 16 GiB RAM,
2 CPUs, 128 PIDs, 16 GiB total working disk, at most 1 GiB data download, $0 new
paid execution**. Suggested disk allocation: 12 GiB preparation inputs, 1 GiB
scratch, 2 GiB outputs, 1 GiB control/log/transfer reserve. These are proposed
stopping limits, not measured requirements or proof that the existing environment
supports them. Dependency/image acquisition requires its own inventory and budget;
the 1 GiB data allowance does not silently authorize unlimited image downloads.
If inventory or sparse-memory estimates exceed the available envelope, hold and
revise before analysis. No automatic retry or larger-resource purchase follows.

## Remaining freeze gates and ownership

| Gate | Owner / next action |
|---|---|
| Current runtime/policy and original prompt binding | OpenAI support/platform; escalation submitted privately, response pending |
| Worker quota, watchdog, termination and recovery | Weft implementation plus platform-supported controls; qualify new canary occurrence |
| Actual matrix feasibility and cell/feature denominators | Weft bounded inspection after the qualified route is available |
| Exact labels, target values and reproduction recipe | Three 50-gene lists inspected and retained; per-cell labels and Fig. 1l inputs/recipe remain unresolved, including the separate larger Source Data workbook |
| Frozen code/environment and measured resource estimate | Weft prepare immutable snapshot/stack and finite reviewed bounds |
| Consequential scientific scope and any changed gate | Owner reviews the completed contract; this draft is not that decision |

No owner action is needed just to keep preparing this draft. When platform support
replies, return the response here; a required replacement/permission change will
be presented concretely. The final scientific review will focus on the descriptive
comparison, unresolved replication limits and measured budget, not Docker flags.
See [worker integration](../qualification/AUTHOR_WORKER_INTEGRATION.md) and
[runtime unblock requirements](../qualification/W08_RUNTIME_UNBLOCK.md).
