# Execution environment: dot and Codex Cloud

**Selected architecture, 11 October 2026:** a dot coordinates Weft; Codex Cloud is
the first-choice runtime for repository commands and the Choi pilot. No additional
physical computer is required. Private `weft-pilot` is published at d031cef;
[setup checks and one small external restore passed](../records/cloud-setup-20261011.json).
[Bounded container controls passed](../records/cloud-runtime-20261011.json) in a
fresh task. The private Drive route passed [independent synthetic cloud restore](../records/cloud-drive-restore-20261011.json).
Full coordinator/Drive job integration, large outputs, retention guarantees, ledger
authority and numerical readiness remain held.
See the [setup runbook](CLOUD_SETUP.md) and [ordered roadmap](IMPLEMENTATION_PLAN.md).

## Why the earlier sizing recommendation changed

The audited local Windows ARM64 desktop has about 15.6 GiB total RAM and had about
2.8 GiB free during the source review; WSL was not installed. These historical
observations remain in the [review receipt](../records/pilot-review-20261011.json).
Existing local research environments remain untouched.

The earlier separate Linux x86-64 / 32-GiB recommendation was conservative sizing,
not a measured minimum or a hardware purchase requirement. Cloud qualification
supersedes it. The setup worker was Linux x86-64 with a 4-core CPU quota, a
32-GiB cgroup memory ceiling and about 29.83 GiB workspace free. These observations
are not platform guarantees or per-job enforcement. Uninterrupted job lifetime
and storage retention remain unknown. Do not transfer the six-hour GitHub Actions
limit to Codex Cloud.

Selected Choi triplets total about 155 MiB compressed (archive about 333 MiB).
Their 46,423,890 stored entries span three matrices with 737,280 raw barcode columns
each. Dense float32 allocation across them would use about 230.7 GiB; this is an
avoidable representation cost. Load sparsely, filter one library at a time and
concatenate only qualified cells. Peak memory/runtime remain unmeasured.

## Deployment contract to qualify

| Surface | Intended use | Before declaring it ready |
|---|---|---|
| Dot cloud computer | Coordination, manual source review, candidate single-writer ledger | Demonstrate dispatch/return, structured-record access, persistence, backup/restore; no assumed SDK |
| Private Codex Cloud environment `weft-pilot` | Pinned Weft commands and later scientific jobs in fresh workspaces | Verify actual architecture/resources, dependencies, network, cancellation and artifact export in a fresh task |
| Public GitHub repositories | Weft code/compact receipts; pinned read-only Ravel context initially | Exact revisions/hashes; no bulk Ravel checkout/LFS smudge, private preferences or scientific data push |
| Private Google Drive folder | Qualified synthetic upload/recovery; future immutable outputs and state backups | [Independent restore passed](../records/cloud-drive-restore-20261011.json); large outputs, retention and ledger authority remain separate checks |
| Local X: archives | Optional existing source/backup | Cloud work must succeed without X: access or an awake desktop |

OpenAI documents dot cloud work and delegation into configured Codex Cloud
environments. Published environments provide fresh task workspaces and saved setup;
important outputs still need explicit saving. These capabilities do not establish
Weft's scientific isolation, resource limits or evidence retention.
[Dot computers](https://learn.chatgpt.com/docs/dots/computers-and-apps),
[cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments).

## Dependency stages

1. **M3a setup:** Python 3.12+ and Git. Current validation, discovery and reading
   code uses the standard library. Record exact versions; no API key or dataset
   is needed for offline checks.
2. **M3b / M2 qualification:** add only dependencies required by the implemented
   job service. Test synthetic jobs, delegation, limits and recovery first.
3. **M4a science:** select/lock the adapter's actual stack (expected NumPy/SciPy,
   pandas, AnnData/Scanpy, clustering, Scrublet and plotting dependencies).
   Import/version/synthetic tests precede data. These are candidates, not an
   installed lock. The 2020 Scanpy/Louvain/manual exclusions are not equivalent
   to modern Leiden/MAD processing; retain the adapted label/discrepancy ledger.

No GPU is required by the bounded count-matrix design. Actual package compatibility
and sparse memory use determine feasibility, not compressed file size.

## Qualification receipt and numerical readiness

Record environment identity/version, task ID, Weft/Ravel commits, timestamp,
OS/architecture, Python/Git and eventual dependency lock; observable CPU, memory,
disk, process/network limits; bounded test scope; measured peak memory/time;
cancellation result; artifact destination, hashes and restoration. Do not expose
credentials/environment variables or private account data. Unknown measurements
remain unknown rather than passing.

Before numerical dispatch require:

- M3 identity, exclusive lease, attempt history, immutable references and resource
  enforcement; duplicate-submission and uncertain-termination tests.
- A new versioned Ravel contract: prior exposure, comparison/unit/endpoint,
  published/adapted QC, annotation criteria, seeds and new output paths.
- Explicit public download or authorized copy, checked against inventoried
  archive/member hashes. A second copy is still the same source data.
- Coordinate/value validity, sample-prefixed barcodes and a bounded sparse-loader
  benchmark permitted by the contract. Preserve frozen historical outputs.
- Verified memory/time bounds and process-tree cancellation, with measured headroom.
  The former 16-GiB cap is not assumed available in the cloud.
- Durable output export/restoration; an in-task success with lost artifacts is incomplete.

Prefer Linux x86-64 if available but inspect the actual runtime. If the selected
cloud cannot satisfy a required control or measured workload, record why and
request a concrete plan revision. Another cloud worker is a fallback decision;
no local PC, paid VM, API account or new storage service is implicitly required.

## Manual deployment update

The owner selected [checkpointed manual execution](MANUAL_PILOT.md). [Dot handoff
and SQLite checkpoint restoration](../records/manual-coordinator-20261011.json)
passed. The [numerical API fixture](../records/numerical-stack-summary-20261011.json)
also passed; real-data memory, a surviving watchdog, contracts and per-job
checkpoint integration still precede science. No workspace-retention guarantee is
assumed. PROGRESS.md owns the current checkpoint.
