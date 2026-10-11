# Scientific execution environment: P001 recommendation

**Recommendation, 11 October 2026: use a separate Linux x86-64 worker for numerical
analysis; retain local Codex on Windows for manual reading and coordination.**
No worker has been selected, installed, rented or started. The owner's manual
Codex reading choice does not select a scientific compute host or authorize spend.

## Evidence behind the recommendation

The observed desktop is Windows 11 Home on an ARM64 Snapdragon X, with eight
cores and about 15.6 GiB total memory. WSL was not installed when checked. An
existing Ravel x64 Python environment runs through emulation, but it is shared
research infrastructure and will not be changed. The recorded observation during this
review had only about 2.8 GiB free RAM; available memory is transient, so every
future launch needs a new check. Exact observations are retained in the
[review receipt](../records/pilot-review-20261011.json).

The [input review](PILOT_CHOI_REVIEW.md) found 46,423,890 stored entries in the
three selected matrices, each with 737,280 raw barcode columns. All three dense
float32 matrices alone would use 230.7 GiB. That is an avoidable representation
cost, not a measured requirement for the intended sparse pipeline. A sparse,
one-library-at-a-time loader with filtering before concatenation is mandatory.
Actual peak memory and runtime have not been benchmarked.

## Options and proposed limits

| Route | Recommendation | Proposed qualification bounds |
|---|---|---|
| Separate Linux x86-64 workstation/server/VM | Preferred for P001 and the later worker | 4 vCPU, preferably 32 GiB host RAM; one job, 16 GiB process/container memory cap, 6-hour wall limit; CPU only |
| New Windows x64 environment on X: | Conditional fallback for a trusted, adapted count-matrix pipeline | One job, 2–4 cores, 6 GiB memory cap; require at least 10 GiB host available RAM at launch; sparse-loader benchmark and enforced cancellation first |
| WSL/VM on this 16 GiB desktop | Defer | Shares the same constrained memory; installation and storage relocation would be a separate decision |
| Ordinary GitHub CI | Keep for deterministic software tests | No raw scientific dataset job or public-PR access to the personal desktop |

These are engineering proposals, not activated or measured resource guarantees.
The earlier pilot's blanket 16 GiB worker allowance is unsuitable for a host with
only 15.6 GiB total memory. A 16 GiB cap remains a proposal only for the separate
32 GiB worker. No GPU is required by the bounded count-matrix design.

Linux x86-64 reduces architecture friction for the older scientific stack and
offers a straightforward place to qualify a contained worker. It does **not**
guarantee that the 2020 software stack can still be reconstructed. Pin and test
the actual versions; if a modern stack is needed, label that route adapted and
record the differences. Windows x64 package compatibility under ARM emulation
must likewise be tested in the new environment rather than assumed from one
existing installation. See [Scanpy installation guidance](https://scanpy.readthedocs.io/en/stable/installation.html).

## Isolation, data placement and qualification

Keep Weft orchestration/cache on `X:/GitHub/weft`. Ravel remains the scientific
owner at `X:/GitHub/ravel`. Reference the existing GSE145031 archive read-only;
copy to a separate worker only through a checksum-verified transfer. A copied
file or a second analysis of it is still the same source data.

Use a fresh, versioned environment and output directory. A Python virtual
environment isolates dependencies, not arbitrary author code or host access
([Python documentation](https://docs.python.org/3/library/venv.html)). Linux worker
qualification must demonstrate a nonprivileged process, read-only input mount,
separate outputs, bounded memory/CPU/time, bounded network access and no publication
credentials. On Windows, [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
are a candidate for process-tree limits; no such runner is implemented yet and
they must not be described as a complete security boundary.

Before the first analysis:

1. Select the actual host and any allowed cost. Do not provision an unchosen host.
2. Implement M3 job identity, exclusive lease, attempt history, cancellation and
   enforced resource limits. Test failures using synthetic inputs first.
3. Create the new Ravel contract/adapter under its governance. Pin input hashes,
   code, dependency lock, seeds, published/adapted methods and new output paths.
   Resolve allowed annotation comparisons and tolerances with recorded review.
4. Validate matrix coordinates/values, sample-prefixed barcodes, sparse storage
   and memory behavior. Benchmark a bounded loader smoke test only after the
   contract permits it; do not silently run the historical scripts.
5. Verify sufficient free memory/disk, input hashes, unchanged frozen outputs and
   process-tree termination. An ordinary environment import is not qualification.
6. Only then dispatch the bounded descriptive run. Preserve all attempts, staged
   denominators, resource receipts and discrepancies; no automatic scientific acceptance.

The Choi review is complete enough to prepare this package. Worker selection,
runtime qualification, a new scientific contract and comparison criteria remain
the boundary before any numerical analysis.
