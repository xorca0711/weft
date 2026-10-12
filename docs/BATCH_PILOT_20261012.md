# Fresh-candidate development test — 12 October 2026

This is a manually operated software integration test of the batch/agent interface,
not a deployed cloud screening service or an independent evaluation of reading
quality. Choi's analysis, ledger, held reservation and publication were untouched.
No numerical analysis, dataset download or Ravel write occurred.

[Machine-readable record](../records/backend-batch-validation-20261012.json) ·
[Complete 74-paper candidate list](../records/backend-candidates-20261012.csv) ·
[Interface and command guide](BATCH_SCREENING.md)

## Frozen search and observed outcomes

The existing `alveolar-transitions` profile and pinned Ravel A0/A1 context were
used unchanged. FIRST_IDATE was 12 September–12 October 2026 inclusive. Limits:
12 search attempts, 100 records per search, five paper/RQ screening packets and
two XML attempts. Broad, contrary and adjacent searches returned 54, 8 and 20
records respectively. All three completed without subdivision. Deduplication
reduced **82 record occurrences to 74 papers / 148 proposed RQ links**.

Selection was lexical paper ID then RQ ID. Five links therefore represented three
papers, not the five highest-priority papers. The agent recorded prior exposure:
these abstracts were first inspected in this task, the RQ context was already
available, and the user's reading history is unknown. No blinded evaluation is
claimed. Full Ravel dossiers were not reviewed for scientific compatibility.

| Paper | Proposed disposition | Screening rationale and boundary |
|---|---|---|
| [Biomimetic Hydrogel Scaffold…](https://doi.org/10.1002/adhm.71751) | A0 hold; A1 hold | Adjacent lung-repair context; the abstract does not establish the transition-state or linked regulatory/outcome comparison these RQs require. |
| [Biofunctionalized Bilayer Hydrogel…](https://doi.org/10.1002/adma.75042) | A0/A1 link rejection | Periodontal bone/ligament repair is a dental “alveolar” match. This rejects the proposed links, not the quality or general value of the paper. |
| [Endowing Flexibility of Alveolar Type II Cells…](https://doi.org/10.1002/advs.77773) | A0 read next; selected text assessment held | The state-conversion model merits reading for A0. Figures, supplement, source lineage and data eligibility remain unreviewed; no shared programme or fate mechanism is accepted. |

The remaining **143 links are deferred**, not rejected or fully screened. All
74 papers remain in the candidate list, including publication types and source
dates. Search coverage is limited to the frozen queries, index and date window.

## What the test verified

- All discovery receipts and source hashes verified. Repeating completed discovery
  made no network request. Each of five identical screening resubmissions returned
  `already_recorded` without another review event.
- The selected paper's open-access XML yielded 82 extracted segments. A four-
  statement assessment of selected text passed identity/locator checks and retained
  `next_action: hold`; resubmission was idempotent. Figure pixels and the separate
  supplement were not inspected. Citation checks do not certify interpretation.
- A private 525,528-byte checkpoint retained 34 files. Every manifest hash, ZIP
  integrity and a fresh read-only SQLite integrity/count check passed. The restored
  database was not activated. This verifies retained state, not remote dispatch,
  path portability, resume from another host or durable cloud storage.
- Focused failure tests cover interrupted searches/reads, incomplete coverage,
  caps, replay, current-state changes, source tampering, locks and response schema
  restrictions. [PR #5](https://github.com/xorca0711/weft/pull/5) Linux CI passed
  all 144 tests without skips on code revision `5915ba7`.

## Issues surfaced and next work

The broad query's bare `alveolar` term admits dental studies. Propose a separately
versioned lung-qualified stream while retaining the adjacent-context search; do
not rewrite this frozen result or exclude all other tissues. Publication types
also require explicit screening: index membership is not proof of peer review.
The lexical sample repeats a paper across RQs and is not efficient prioritization.
Evaluate a paper-level reading cache and stream-aware ordering with independent
low-ranked/contrary-paper review before selecting a production policy.

B1 coordination and B2 packet/response mechanics are implemented. B2 cloud-agent
handoff and B4 remote recovery remain unqualified; this is only the local B4
development demonstration. In particular, cached XML directories need explicit
reconciliation when moved between hosts. B3 figure/supplement/dataset gates and
B5 independent evaluation/recurrence remain open. Keep the selected dot/Codex
Cloud route; no new credentials, paid API, schedule or deployment were activated.
