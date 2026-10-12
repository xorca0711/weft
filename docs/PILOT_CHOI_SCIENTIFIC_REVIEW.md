# Choi P001: scientific review and integration disposition

**12 October 2026: review complete; complete-output publication and human review
remain open.** Ravel owns the [full scientific assessment](https://github.com/xorca0711/ravel/blob/714945697b007f4a0046834b34251392c1cfbe5a/Research%20Article/gate1_02_choi_2020/weft_pilot_v1/SCIENTIFIC_REVIEW.md). Weft records
the review handoff, automation limits and remaining integration conditions. The
original analysis executed once and was not rerun for this review.

## What was checked

The original 15 output hashes, saved H5AD, cell identifiers, count/mitochondrial
QC, composition denominators, marker fractions, clustering tables and saved
neighbor diagnostic reconcile across **1,497 read-only assertions**. All five
PNG figures were visually inspected against the audited Choi Fig. 1/S1 and source
methods. See the [review record](../records/choi-scientific-review-20261012.json)
and [unchanged execution/transfer evidence](../records/choi-figure1-execution-20261012.json).
This is internal consistency checking and agent interpretation, not biological
replication, an author-label benchmark or human scientific acceptance.

## Findings and limits

- **11,683 post-doublet cells**; **10,399** remain in composition denominators
  after 1,284 pipeline contaminant labels. One pooled two-mouse library per
  condition prevents animal-level inference and confounds timepoint with library.
- Four alveolar labels are recovered at the fixed primary resolution. **pAT2 is
  absent**, including after the prescribed conditional subclustering. All marker
  genes are available; this is failure to recover the label, not evidence that
  the paper's primed AT2 population does not exist.
- Coarse patterns resemble the paper: PBS AT2-like dominance, increased day-14
  cycling/DATP labels and a larger day-28 AT1 fraction. The pilot's DATP fractions
  are 0.40%, 18.71% and 8.87% of non-contaminant cells. Exact five-state
  reproduction and mechanistic claims are unsupported.
- Day-28 exclusions are **28.06%** of post-doublet cells, mostly club/airway
  labels with substantial AT2 identity-marker detection. Their status as true
  contaminants is unresolved; changing the denominator materially changes fractions.
- DATP/AT1 are separately labelled only at resolution 1.0, not 0.3/0.5.
  **520/917** DATP-labelled cells fall in hAT2-labelled subclusters but remain
  DATP under the frozen retention rule. No relabelling or parameter tuning occurred.
- Published Fig. 1D is a relative-expression/detection **dot plot**; S1B-C are
  heatmaps. Earlier pilot shorthand called Fig. 1D an expression heatmap. Ravel's
  review corrects that terminology without changing frozen source/contract bytes.
  The pilot heatmap displays marker-set mean detection and cannot establish
  cytokine activity, metabolic flux, regulatory state, lineage or repaired tissue.
- Frozen plots retain presentation issues: alphabetical time order, clipped
  y-labels and different color mappings between library/timepoint panels. Use the
  chronological numeric table and panel-specific legends in Ravel's review.

## Candidate and milestone disposition

**No new RQ or mechanistic phenotype is proposed.** A0's stopped cross-tissue
transfer and A1's missing regulatory-state/later-output link are unchanged.
The article-local result is suitable for a bounded discrepancy record in the
decision buffer; it does not directly become support for a canonical claim.
This is not a human retain/reject decision or an evaluation of unseen-paper screening.

M4b execution, artifact recovery and scientific review are complete for the
single attempt. **M5 integration remains open:** Ravel PR #149 stays draft and
the original numerical receipt remains unregistered until every declared output
has a reviewed, durable publication route. The 385,675,968-byte H5AD is included
in private verified recovery but has no qualified clean-clone CI publication route.
Do not omit it, edit the receipt, weaken the validator or activate paid storage.

The coordinator's last independently verified backup remains the 30-event
`c8ac521d…` checkpoint. This local review did not change its ledger or release
its reservation. Before another job, reconcile the review, publication disposition
and authority in the same coordinator and make a verified checkpoint. No new
dispatch, analysis retry, automatic acceptance, schedule or unseen-paper pilot
was initiated. Source pins, all attempts and original outputs remain preserved.
