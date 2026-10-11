# Current project state

## Discovery and manual reading checkpoint — 11 October 2026

Implemented on `codex/discovery-review-buffer-20261011` against Weft main
`59aa0f740b8e3d6d856684ef7052f5e7d77b7820`. Ravel main was freshly rechecked at
`bfe26b876221cf6c6fa6f9b16a90cfb516b5998d`; its files/worktrees were not changed.
The owner selected **local Codex with manual runs** for the reading stage.

Completed: bounded Europe PMC adapter; strong-ID deduplication and identity holds;
raw response/cursor/hash receipts; completed-window cutoffs and overlap; read-only
context for all 32 registered RQs; initial A0/A1 profiles; persistent proposal buffer
and reading-priority decisions; open-access XML packets and source-locator checks;
README workflow and synchronized implementation/gate documentation.

Validation: **58 tests passed**, 35 documentation links checked, all 15 pinned
Ravel source blobs verified. Seven live searches produced 17 verified raw pages.
The Choi historical query recovered five records over three pages, including the
target DOI; repeating it preserved candidate IDs. The recent title/abstract query
found six records for 4–11 October. Contrary and priority-journal queries returned
zero in that window. Wider searches remained explicitly truncated; they did not
advance cutoffs. See [live receipts](records/discovery-validation.json).

The first unrestricted recent query produced 8,952 reported matches and was capped
at 20. Inspection also found acronym noise in the historical query. A revised
recent title/abstract profile reduced the reported yearly set to 819; it too was
capped at 20. These are observed query results, not relevance or recall metrics.
The original attempts remain retained. Initial profiles do not cover all 32 RQs.

The Choi XML packet contains 160 source segments. A manual assessment of selected
results, caption and methods yielded four source-bound statements, including
two-mouse pooling. Hash/locator checks passed; semantic scientific acceptance was
not issued. [Reading assessment](records/pilot-reading-20261011.json) records its
limited coverage and hold. Figure pixels, separate supplements, fresh GEO input
mapping and the scientific reproduction remain incomplete. No numerical analysis,
new RQ, model launcher, API account or scheduled automation was activated.

## Next steps and decision point

1. Review/merge the discovery implementation, especially buffer and authority
   boundaries. Local records are not an authenticated approval system.
2. Complete the pilot's figure/supplement inspection and data/sample inventory;
   evaluate source-support judgments against an independently reviewed set before
   claiming M2 screening quality. Full version-family and correction-feed handling
   also remain unqualified.
3. Choose the scientific worker before implementing its execution route: a new
   isolated Windows environment on X: or a separately provisioned Linux worker.
   Local inspection found the existing Ravel x64 Python environment; WSL reported
   that it is not installed. Do not install WSL, alter that shared environment or
   start resource-heavy analyses as an implicit consequence of discovery work.
4. Implement M3 job leases/resource accounting and freeze a new Ravel contract,
   input hashes, environment and justified published-result comparison tolerance.
   Then run the bounded descriptive pilot through Ravel's gate with separate outputs.
5. Build the reviewed export only after successful qualification. No automatic
   merge, claim acceptance or canonical registration is implemented.

Raw responses/XML and SQLite state are in ignored `runs/discovery` under the Weft
checkout on X:. Public records contain queries, hashes, metadata and short original
assessments only. The Ravel directory migration remains deferred. Initial bootstrap
records remain historical; current CI and the implementation PR own remote status.
