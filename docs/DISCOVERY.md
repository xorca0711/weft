# Literature discovery

The standard-library Europe PMC adapter is implemented for explicit manual runs.
No API key or model is required. Run commands from the Weft checkout; local raw
metadata, abstracts, XML and SQLite state remain in ignored `runs/` on that drive.
Use `--store` for a different provisioned persistent location. Do not put these
files in the OS-drive Codex home or commit full articles to the public repository.

## Commands

```bash
python -m weft context --repo /path/to/ravel --output runs/rq-catalog.json
python -m weft discover --repo /path/to/ravel --profile choi-pilot --since 2020-01-01 --until 2020-12-31 --page-size 2 --max-records 40
python -m weft discover --repo /path/to/ravel --profile alveolar-transitions --since 2026-10-04 --until 2026-10-11
python -m weft buffer-list
python -m weft verify-discovery --run SEARCH_RUN_ID
```

The context builder resolves all 32 questions at the pinned revision; initial
manually authored search profiles cover A0/A1 and Choi, not the full portfolio.
Add a reviewed profile for another registered RQ. The packet includes canonical
wording and current evidence locators; it does not claim to have read all dossiers.
Both config/profile changes and the lock update should be reviewed before use.

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

## Verification

Offline tests cover pagination, retry/failure distinctions, date windows, duplicate
and conflicting identities, stale links, hash tampering and reading boundaries.
[Live validation](../records/discovery-validation.json) records actual queries,
counts and hashes. It is an engineering smoke test, not a recall/precision study.
An exposed historical hit and zero contrary hits do not qualify autonomous screening.
