# Literature discovery

New CLI scans now apply the [mechanism-focused primary-list scope](PRIMARY_PAPER_LIST.md).
Named CNS journal membership and biological query constraints narrow retrieval;
source-bound screening still determines reading admission. Standalone receipts
bind the policy and cannot bypass the scoped review route through manual reading.
Historical receipts and the source profiles below remain unchanged.

The standard-library Europe PMC adapter is implemented for explicit manual runs.
No API key or model is required. Run commands from the Weft checkout; local raw
metadata, abstracts, XML and SQLite state remain in ignored `runs/` on that drive.
Use `--store` for a different provisioned persistent location. Do not put these
files in the OS-drive Codex home or commit full articles to the public repository.

## Commands

```bash
python -m weft context --repo /path/to/ravel --output runs/rq-catalog.json
python -m weft profile-coverage --repo /path/to/ravel
python -m weft discover --repo /path/to/ravel --profile choi-pilot --since 2020-01-01 --until 2020-12-31 --page-size 2 --max-records 40
python -m weft discover --repo /path/to/ravel --profile alveolar-transitions --since 2026-10-04 --until 2026-10-11
python -m weft buffer-list
python -m weft verify-discovery --run SEARCH_RUN_ID
```

The context builder resolves all 32 questions at the pinned revision. The original
A0/A1 and Choi profiles remain unchanged. Thirty additional opt-in profiles for
A2–A31 are marked `draft-unqueried`, with broad, alternative and adjacent streams,
exact source/context bindings and per-question limits. No retrieval quality or
recall is established for them. The packet includes canonical
wording and current evidence locators; it does not claim to have read all dossiers.
Both config/profile changes and the lock update should be reviewed before use.

`profile-coverage` prints an offline JSON audit against the complete pinned
RQ catalog. The Python API is `weft.coverage.audit_profiles(configuration, context)`;
pass the complete `build_context(repo, lock)` result to expose portfolio gaps. The report lists
unconfigured RQs, first-index versus historical profiles, draft status/count,
missing complementary streams and identical query reuse. It validates references and records hashes;
it does not invent biological queries, certify profile review, measure recall or
start a search. A configured question is not a comprehensively searched question.

Both retrieval commands check a selected draft's source/context binding before
opening a store or requesting metadata. A changed Ravel pin requires explicit
review and a new binding. Profile selection is explicit; adding these drafts
does not queue a portfolio-wide search or activate scheduling.

`broad` is the default stream. `rq_contrary` and `adjacent_context` complement it.
`priority_journals` requires an explicit start date and a completed broad run in
the same store covering that window and context. Priority titles do not confer
eligibility. Returned ISSNs are preserved; journal aliases/publisher-family
expansion are not qualified. Career preferences are not used by this adapter.

## Search coverage and recovery

Recent discovery uses `FIRST_IDATE` (first indexed), historical replay uses
`FIRST_PDATE` (first published). A later run can omit `--since` to reuse its query/
context-specific completed cutoff with seven days of overlap. Query/context
changes get separate streams. Explicit windows cannot skip a known gap and advance
the same cutoff. Initial cutoffs cover only their stated window, never earlier
truncated backlogs. The explicit end date is inclusive and recorded in each receipt.

Responses retain URL/query, cursor, API version, UTC time, retries, raw SHA-256 and
deduplication artifacts. There are at most three HTTP attempts, 30-second request
timeouts, a bounded Retry-After delay, an 8 MiB response cap and at most 200 records
per CLI search. Only complete, stable retrieval advances a cutoff. HTTP errors,
malformed bodies, missing/repeated cursors and changing result sets cannot masquerade
as a successful zero-hit search. Partial metadata remains inspectable.
Inconsistent per-page hit counts and malformed cursors are retained as malformed
responses. Aggregate overcounts during index changes remain explicitly unstable.

Exit code 0 means the requested operation completed, 1 means validation failed,
and 2 denotes a stored error, truncated/unstable retrieval or reading hold.
Split an oversized window into explicit smaller windows; preserve the truncated
attempt. There is no automatic partitioner or durable scheduler yet. If interrupted,
repeat the saved window in a new run; old files are never overwritten. Reading
dispatch requires a complete recent source run. Cutoff commits serialize through
SQLite; this does not implement scientific job leases or multi-host coordination.

First-index dates do not monitor all later corrections. Re-fetch candidate metadata
before scientific screening/promotion; this release only enforces a seven-day age
limit before preparing a reading packet. Provider correction flags and version
relations are preserved, but absence of a flag is not integrity clearance. Crossref,
publisher correction feeds and complete version-family resolution remain future work.

## Bibliographic relation reconciliation

New discovery runs retain explicit Europe PMC correction/version links, their
exact target identifiers, source locators and provider qualification notes.
Relations do not join distinct paper identities. Title matches remain nominations;
a provider's heuristic preprint link remains a provider assertion, not verified
edition equivalence or independent replication.

The candidate buffer now reconciles these links across all retained observations.
An explicit correction/retraction relation places its source and exact-ID target
candidates on an attributable metadata-integrity hold, including an original that
was previously marked `read_next` or discovered before the notice. The original
review event remains unchanged. The new event invalidates an outstanding screening
packet. A missing notice in a later response cannot silently release the hold;
disposition requires a separately reviewed resolution mechanism. Ordinary comment
or version links are visible review nominations and do not by themselves make a
scientific determination or integrity hold.

Reconciliation is idempotent and runs within the existing store transaction, with
no destructive schema migration. Historical observations and receipts remain
unchanged. Source contradictions within MED/PMC identifiers are now held rather
than silently resolved; PMC provider IDs also supply their explicit PMC identity.
For such affected historical records, obtain new metadata and review rather than
rewriting a frozen packet to fit the updated normalization. Unidentified relation
targets remain visible in the deduplication artifact; no title-based target is guessed.

## Verification

Offline tests cover pagination, retry/failure distinctions, date windows, duplicate
and conflicting identities, stale links, hash tampering and reading boundaries.
Additional synthetic regressions cover correction-before/original-before ordering,
cross-RQ propagation, preserved decisions, stale packets, repeated-source idempotence,
source self-identifier conflicts, provider notes and query-configuration gaps.
[Live validation](../records/discovery-validation.json) records actual queries,
counts and hashes. It is an engineering smoke test, not a recall/precision study.
An exposed historical hit and zero contrary hits do not qualify autonomous screening.

For coordinated multi-stream searches and structured agent responses, use the
[batch interface](BATCH_SCREENING.md). Lower-level commands remain available; do
not run competing coordinators against a shared store.
