# Connection to Ravel

## Single ownership

Ravel owns questions, paper namespaces, literature context, source contracts,
scientific scripts, run receipts, results and acceptance decisions. Weft owns
source discovery, agent orchestration, operational policy and job records.
No copy of the canonical RQ register is maintained as a second authority.

The initial connection is read-only and pinned by
[`integration/ravel.lock.json`](../integration/ravel.lock.json). Its commit is
the main revision inspected during preparation. Selected Git blobs have SHA-256
hashes; the verifier also checks that referenced RQ IDs exist in that registry.
No local absolute path, private note or credential is stored in the manifest.

## Read, run and return

1. Resolve an explicit Ravel commit and verify manifest hashes. Build bounded
   context packets from its registry, current reports and amendments.
2. Write the job proposal in Weft: paper version, context hash, purpose, requested
   comparison, exposure, source lineage, operational limits and adapter version.
3. In a separate Ravel branch/worktree, add the new scientific contract and any
   scoped analysis adapter. Follow Ravel's instructions; commit/freeze the contract.
4. Execute through Ravel's existing runner on an isolated worker:

   ```bash
   python analysis/scripts/research_gate.py run path/to/contract.json --run-id UNIQUE_RUN_ID
   python analysis/scripts/research_gate.py verify analysis/research/runs/UNIQUE_RUN_ID/receipt.json
   ```

   These are future templates, not instructions to rerun an existing historical
   script. The actual paths and run ID come from the qualified contract.
5. Weft records the Ravel commit, contract/run IDs, artifact hashes and receipt
   status. Large raw inputs remain in configured data storage.
6. The exporter creates a PR carrying the scientific files and current summaries
   in Ravel. Weft stores the package manifest and PR identity, avoiding duplicated
   numerical authority. Verify the current integration base and resolve changes
   explicitly; never force-push over unrelated work.
7. Record the actual merge commit before labeling an export integrated. Canonical
   question registration or claim promotion requires its recorded authority.

## Proposed exchange envelope

Required fields: `schema_version`, `job_id`, `paper_id`, `paper_version`,
`weft_commit`, `policy_hash`, `ravel_base_commit`, `rq_context_hashes`,
`contract_path`, `contract_sha256`, `input_manifest_sha256`, `run_id`,
`receipt_path`, `receipt_sha256`, `source_lineages`, `artifact_manifest`,
`outcome`, `interpretation_limits`, `review_state` and `integration_pr`.

Before execution some fields are absent by stage; the state machine must forbid
using a proposal as a completed receipt. Do not fill required evidence with
invented values. Candidate IDs belong to the paper/job namespace until registered.

## Permissions and storage

Use separate credentials for read/search, compute and PR preparation, only when
those stages are activated. A worker does not need repository administration or
merge rights. Public CI must not execute untrusted fork code on the local machine.
Private career notes are never bundled into Ravel context or public exports.

Use `WEFT_DATA_ROOT` for downloaded data and `WEFT_RUN_ROOT` for operational runs.
Ravel source files and data remain where they are until an explicit migration.
Avoid copying existing large datasets: use a verified read-only input reference
when the worker can access them; record real file identities and checksums.

## Drift

A newer Ravel main does not silently retarget a job. Propose a lock update with
the changed contexts/results and invalidate affected queued jobs. Before export,
compare against the current integration base; rerun only checks affected by changes.
Historical jobs retain their exact revision. Hash verification proves byte identity,
not scientific correctness or currentness.
