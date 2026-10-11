# Current project state

**Update this before stopping work, every session.**

## Cloud setup published; M3 controls incomplete — 11 October 2026

Private **weft-pilot** was configured and published through the actual UI at the
owner-requested PR #1 commit `d031cef02ab4a417760bca46e90a63917d215d31`.
The account-access issue is resolved. [Setup evidence](records/cloud-setup-20261011.json)
records 58 passing cloud tests, offline validation, all 15 pinned Ravel files,
exact-pin restoration after clean repository refresh and preservation of dirty work.
The observed Linux x86-64 worker has a 4-core CPU quota, 32 GiB memory ceiling and
about 29.83 GiB workspace free; these are measurements, not service guarantees.
Ravel remains a bare source cache at `bfe26b876221cf6c6fa6f9b16a90cfb516b5998d`.
No bulk checkout, LFS download, new credentials or network expansion was needed.

The existing synthetic ZIP was transferred as a rendered base64 envelope and
independently restored on Windows. Archive SHA-256, ZIP CRC, member inventory and
artifact SHA-256 passed. No archive code ran. The file viewer's Save As action did
not produce a confirmed download. This proves one small setup export, not durable
cloud storage, bulk output export or operation without an awake PC. The immutable
cloud receipt and independent restore receipt are in ignored
`runs/cloud-setup-20261011`; publication and restore extend the earlier held receipt.

PR #1 remains unchanged. Follow-up work is isolated in
[PR #2](https://github.com/xorca0711/weft/pull/2),
`codex/cloud-job-controls-20261011`, stacked on PR #1. The
[synthetic job ledger](docs/JOB_CONTROLS.md) implements stable identity, verified
input hashes, transactional single-slot claims, append-only events, unknown-outcome
holds, cancellation requests and bounded retries. All **72 tests passed**, with
both CI checks passing for the implementation commit. Terminal reports remain
self-reported; there is no scientific dispatch or successful-completion API.

## Exact next steps and open dependencies

1. Fresh-task source checks passed (58 tests / 15 Ravel blobs). Its configuration
   version suffix matches published `cecfgver_6acb61fdc96481a283a745de16ae40ce`;
   per-task environment IDs/revision counters differ. [Synthetic runtime receipt](records/cloud-runtime-20261011.json)
   verifies 256-MiB memory, no extra swap, 32 PIDs, 1 CPU, no network, non-root,
   read-only root, deterministic output, OOM/PID failure and process-tree cancellation.
   No disposable containers remain. The startup skill was absent from the catalog,
   so the cached preflight was explicitly run; do not rely on automatic injection.
   Platform network enforcement remains unknown, separate from proven container
   isolation. Preserve that hold; use an explicit pinned preflight in the executor. The published d031cef environment remains the baseline;
   a follow-up revision requires explicit versioned selection, never moving HEAD.
2. Finish M3 verified executor receipts, output manifests, enforced memory/time/PID
   limits and process-tree cancellation. Qualify one authoritative ledger and
   recoverable cloud output destination; independent task-local SQLite copies do
   not coordinate jobs. Do not mistake the tiny text export for bulk storage.
   The owner selected a **private Google Drive folder**, with cloud access qualified
   first. Cloud search succeeded, a new owner-only folder was created, and a
   48,400-byte synthetic ZIP was uploaded once and retrieved with matching SHA-256
   and ZIP CRC. [Drive receipt](records/cloud-drive-20261011.json) proves same-task
   roundtrip; [independent cloud restore](records/cloud-drive-restore-20261011.json)
   then passed SHA-256, all 32 CRC/path checks and 12 included source/command hashes.
   cached_setup.sh was not in the archive and its digest remains unverified.
   The test used no PC or source-task files; it does not promise retention or claim
   the desktop was literally powered off. Locators remain in ignored
   private/cloud-artifacts.json. No new credentials or sharing changes.
3. Qualify one manual dot handoff, dispatch/return and hold handling after the
   controls exist. Dot selection/delegation and unattended operation remain open.
4. Prepare a new Ravel contract/adapter, dependency lock and comparison criteria.
   Qualify public inputs against the reviewed hashes, coordinates/values, joins,
   sparse-loader memory and enforced limits before numerical execution.
5. Run P001 Figure 1B-D only when readiness passes, then propose a scoped Ravel PR.
   No pAT2 call or no new RQ is legitimate. No population inference is supported
   by one pooled library per condition. Scientific acceptance remains separate.

Completed baseline: manual discovery/dedup, pinned context for all 32 RQs (initial
queries A0/A1), decision buffer, XML reader and Choi main-figure/S1-S7/input audit.
See [source review](docs/PILOT_CHOI_REVIEW.md),
[review receipt](records/pilot-review-20261011.json) and
[input inventory](records/pilot-inputs-20261011.json). Frozen source records remain
unchanged. M1 correction/version/recall and M2 independent screening evaluation
remain unfinished. Choi is an exposed historical benchmark, not an unseen test.

No Choi analysis, Ravel write, claim acceptance, paid fallback, schedule or merge
was activated. Policy flags and scientific validators remain unchanged. The
[roadmap](docs/IMPLEMENTATION_PLAN.md) owns milestone exits; prior decisions remain
in [DEVELOPMENT.md](DEVELOPMENT.md). Local Ravel worktrees/data are preserved.
