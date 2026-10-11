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
| 2026-10-11 | Dot coordination and Codex Cloud execution; cloud-first roadmap | Owner selected architecture after Codex proposal | Owner for architecture; scientific acceptance pending | Update plan and request access/dependencies; no extra local PC | Cloud execution addresses hardware constraints; no paid fallback or schedule authorized |

## Rejected or substantially revised AI proposals

| Date | Proposal | Why changed | Changed/rejected by |
|---|---|---|---|
| 2026-10-11 | Private initial repository | Owner explicitly chose public; personal configuration remains excluded | Owner |
| 2026-10-11 | Blanket 16 GiB local worker allowance | Audited Windows host has about 15.6 GiB total memory; recommend separate 32 GiB Linux host or a qualified 6 GiB Windows fallback | Codex revision; host selection pending owner decision |
| 2026-10-11 | Treat the Choi pilot as exact reproduction before qualifying methods | Published Louvain/manual exclusions and Ravel Leiden/MAD/annotation rules differ; exact author-cell set is unresolved | Codex revised proposal to explicitly adapted descriptive reanalysis |
| 2026-10-11 | Separate Linux worker as the default next decision, preferably 32 GiB RAM | Owner cannot add a PC and selected dot/Codex Cloud; 32 GiB was unmeasured conservative sizing. Qualify cloud first | Owner selected direction; Codex revised deployment stages |

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

## Cloud execution roadmap — 11 October 2026

The owner selected dots/Codex Cloud and confirmed Create environment and the Weft
repository selector are available. Codex updated the implementation stages,
README workflow, environment requirements, pilot metadata and cloud setup handoff.
The change supersedes unmeasured hardware sizing without altering gate semantics.
No environment, dot task, scientific run or schedule was launched. All existing
source receipts remain immutable. Runtime qualification, product-usage budgeting
and durable ledger/artifact handling remain implementation work.

## Cloud setup and synthetic ledger — 11 October 2026

The owner explicitly requested UI environment setup at d031cef, publication after
successful checks, and continuation toward Choi. Browser account access is pending
resolution. Codex implemented a bounded synthetic-only M3 foundation while waiting;
no execution gate was weakened or scientific authority invented. The new ledger
records cooperative transitions and cannot establish real process termination.

## Published setup and independent restore — 11 October 2026

Account access was resolved. Codex configured private weft-pilot in the UI using
the exact authorized d031cef baseline, reviewed 58 cloud tests and 15 pinned Ravel
blobs, and published after setup and independent synthetic restore checks passed.
The archive was transferred via rendered base64 after the file-viewer download
was unconfirmed; its checksums/CRC were verified on a separate Windows host.
This is narrow setup evidence, not a durable cloud artifact service. Initial
receipts remain unchanged; the new public record distinguishes those observations
from outstanding M3/M4 controls. No scientific gate, source contract, Ravel file,
activation flag or scientific result was changed. No merge is claimed.

Fresh-task qualification independently matched the published configuration version
suffix and passed Docker memory/PID/network/non-root/read-only/cancellation checks.
The owner selected private Google Drive. A new owner-only folder and authenticated
48,400-byte same-task roundtrip passed; a separate cloud restore is being verified.
Private Drive locators remain ignored. Startup skill discovery and managed-network
status differ from setup; receipts retain those limitations rather than claiming
complete M3 readiness. The exact d031cef environment baseline remains unchanged.

Independent cloud-to-Drive-to-fresh-cloud restoration then passed SHA-256, 32
member CRC/path checks and all 12 included source/command hashes. No PC/source-task
files or archived code were used. One referenced setup-script digest cannot be
checked because that file is absent from the ZIP; this limit remains explicit.
This qualifies the demonstrated synthetic recovery path, not retention guarantees,
large scientific artifacts or a shared authoritative ledger.


## Trusted synthetic executor — 11 October 2026

The owner authorized code/tests/docs on PR #2 from exact 1866f96, superseding the
qualification task's read-only source restriction. Codex implemented a fixed-fixture
Docker adapter and strict content-addressed receipts/restoration. Published d031cef
setup and frozen qualification artifacts remain unchanged. Hashes establish content
integrity under a trusted adapter/coordinator; they do not establish actor authority
or scientific success. Executor-bound attempts cannot use legacy self-report release.

The local success/failure/cancellation/unknown distinction is implemented and tested;
whole-job completion, coordinator authority, Drive transport integration and product
dispatch remain unimplemented. Actual bounded success/cancellation used the qualified
cached image without repeating the broad capability probes. 94 tests and offline
validation passed. Public files contain no Drive folder/owner details or raw logs.
No scientific gate, activation flag, Ravel source or environment configuration changed.
