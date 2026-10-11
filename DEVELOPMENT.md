# Development and decisions

## AI assistance

OpenAI Codex prepared the initial documentation, configuration, source-pin
manifest, offline validation code and tests. The owner requested the project
and public creation. No biological analysis was executed by Weft. Completion
of implementation or scientific acceptance has not been claimed.

## Responsibility record

| Date | Item | Proposed by | Decided by | Decision | Reason |
|---|---|---|---|---|---|
| 2026-10-11 | Separate repository with implementation plan and README diagram | Owner | Owner | Requested | Develop the literature-to-reanalysis workflow alongside Ravel |
| 2026-10-11 | Public visibility | Codex offered options | Owner | Public from the start | Explicit response in the creation task |
| 2026-10-11 | Weft name, architecture and Choi benchmark | Codex | Pending owner review of details | Implemented as initial proposal | Natural relationship to Ravel; known successes and limitations make an auditable pilot |
| 2026-10-11 | Complete Choi figure/supplement/data review and recommend a worker before analysis | Owner | Owner requested scope; scientific acceptance remains unissued | Review implemented on existing PR; worker recommendation awaits selection | Preserve the reading/execution boundary and qualify actual input shape |

## Rejected or substantially revised AI proposals

| Date | Proposal | Why changed | Changed/rejected by |
|---|---|---|---|
| 2026-10-11 | Private initial repository | Owner explicitly chose public; personal configuration remains excluded | Owner |
| 2026-10-11 | Blanket 16 GiB local worker allowance | Audited Windows host has about 15.6 GiB total memory; recommend separate 32 GiB Linux host or a qualified 6 GiB Windows fallback | Codex revision; host selection pending owner decision |
| 2026-10-11 | Treat the Choi pilot as exact reproduction before qualifying methods | Published Louvain/manual exclusions and Ravel Leiden/MAD/annotation rules differ; exact author-cell set is unresolved | Codex revised proposal to explicitly adapted descriptive reanalysis |

Future reviews append decisions and rejections rather than overwriting them.
Repository creation does not mean every scientific or operational proposal has
been accepted. No software license has yet been selected by the owner; public
visibility alone does not grant an open-source license.

## Discovery and buffer implementation — 11 October 2026

The owner requested milestone execution and assessment of direct RQ coupling.
Codex implemented bounded retrieval, conservative bibliographic identities,
persistent receipts/cutoffs, pinned RQ context and a review buffer. The owner then
selected local Codex with manual runs for the reading stage. This authorizes that
implementation choice, not scientific claim acceptance or a compute budget.

The revised design places a proposal buffer between query matching and Ravel
evidence. Changed sources/context require renewed reading review. Different
publication editions remain separate until reconciled; no study count is inferred.
The original unrestricted recent query was retained as a truncated attempt and
replaced by a title/abstract profile after observing acronym-related noise.

Scientific gate semantics and buffer boundaries are explicit review items in the
implementation PR. No Ravel governance check was weakened or biological rerun
performed. Automated tests and source locators validate software properties only.

## Choi source and input review — 11 October 2026

Codex inspected all main figures and S1-S7, reconciled the official supplement
with the institutional edition, mapped three GEO accessions and checked the local
GSE145031 archive. No scientific pipeline was executed. The original XML reading
record remains immutable; a new review record extends its coverage. Download
failures and the corrected cover-page alignment remain in local receipts.

The README's implementation descriptions now use the document convention's
"Descriptive only" status; this is a vocabulary correction, not scientific
validation. The roadmap separates the completed manual review from M2 evaluation,
M3 runtime enforcement and M4 numerical work. Ravel's completed directory migration
is reflected in the handoff. Governance, validators and activation flags are unchanged.
