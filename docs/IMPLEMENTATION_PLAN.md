# Implementation plan

## Objective and selected execution route

Build an agent-operated system that discovers papers, reviews relevance, qualifies
reusable data, runs bounded reanalysis and proposes traceable evidence for Ravel.
Missing evidence produces a hold; a completed job does not confer scientific acceptance.

**Owner-selected direction, 11 October 2026: a dot coordinates; Codex Cloud runs
versioned code and scientific jobs after qualification. No additional local PC is
required.** Local Codex remains available for development and manual review. The
prior local-reader choice describes the completed baseline, not a requirement
that future computation remain local. See [the decision record](../DEVELOPMENT.md).

The first end-to-end release finishes when [P001](PILOT_CHOI_2020.md) produces a
reviewable Ravel evidence package, including its unreplicated-effect hold and a
candidate/no-candidate disposition. A positive phenotype or new RQ is not required.

## Responsibility and deployment

| Component | Assigned responsibility | Evidence / implementation boundary |
|---|---|---|
| Dot | Coordinate bounded tasks, source reading, holds and reports through supported product delegation | Structured dispatch/return records; no assumed dot SDK or unattended integration |
| Weft | Discovery, pinned RQ context, proposal buffer, gates, job ledger and export preparation | Discovery/buffer/manual reader implemented; job service and export still to build |
| Codex Cloud | Execute tested repository commands in a qualified published environment | Exact source/dependency versions, input/output manifests, QC and resource receipts |
| Ravel | Canonical RQs, contracts, analysis code, results and acceptance history | Read-only pinned context initially; later scoped, reviewed PR |
| GitHub CI | Deterministic software/document checks | CI status; no scientific compute or desktop runner |
| Local X: storage | Existing archives, optional development and downloaded backups | Not a dependency of a cloud task; never assume X: exists remotely |

One coordinator is sufficient. Separate roles do not require separate agents and
are not independent biological replication. A source match enters the
[decision buffer](DECISION_BUFFER.md); it never directly becomes a supporting claim.

## Development stages and exit criteria

Keep M0-M6 identifiers so existing receipts retain their meaning. M3/M4 are split
into implementation slices below; these are not new scientific gates.

| Order / milestone | Work and deliverable | Exit criterion | Current status |
|---|---|---|---|
| 0 / M0-M2 baseline | Foundation, bounded discovery/dedup, pinned RQs, manual reader, Choi source review | Reuse recorded tests/audit and preserve unresolved limits | Implemented baseline; M1 version-family/recall evaluation and M2 independent screening evaluation remain open |
| 1 / M3a cloud setup | Private `weft-pilot`; exact Weft PR revision; read-only Ravel pin; Python/Git/network preflight | Fresh cloud task passes offline checks and pin verification; capability/access receipt recorded | Next; owner confirmed environment creation and Weft repository availability |
| 2 / M3b job and artifact control | Single authoritative ledger, job keys, leases, append-only attempts, checkpoint/export, cancellation and enforced limits | Synthetic duplicate, expired lease, changed hash, stale context, disconnect, cancellation and restore tests pass | Not implemented; can develop locally alongside setup |
| 3 / M2 cloud coordinator qualification | One manual dot delegation, source-bound reading, structured return and hold handling | Dot uses the selected environment/revision and verifies receipts without bypassing holds; independent screening evaluation remains separate | Planned; no schedule or assumed API integration |
| 4 / M4a scientific readiness | New Ravel contract/adapter, dependency lock, comparison criteria, verified transfer and sparse-loader benchmark | Coordinates/values and joins pass; measured memory fits enforced limits; artifact export/restore passes | Structural input audit complete; contract/runtime unqualified |
| 5 / M4b Choi pilot | Figure 1B-D descriptive adapted reanalysis, exposure record and discrepancy ledger | Complete QC/denominators, all attempts and limitations; no population inference from one pooled library per condition | Not run |
| 6 / M5 reviewed integration | Precedent review, candidate/no-candidate disposition, manifest, scoped Ravel PR and CI | Current Ravel base checked; evidence traceable; acceptance/merge recorded separately | Planned |
| 7 / M6 prospective operation | Freeze unseen-paper evaluation; assess recall, source support, recovery and usage; then propose recurrence | Reviewed criteria met and cadence/scope/usage authority recorded | Planned; automation disabled |

Each slice needs scoped changes, tests and observed limitations. Resolve correction/
version-family coverage and independent screening evaluation before claiming
M1/M2 qualification or unattended operation. Choi remains an exposed benchmark.

```mermaid
flowchart TD
    B["Completed: discovery, buffer and Choi source audit"] --> C["M3a: configure and test Codex Cloud"]
    C --> J["M3b: job ledger, limits, cancellation and artifact restore"]
    J --> D["M2: qualify one manual dot delegation"]
    D --> K["M4a: review contract, lock dependencies and benchmark sparse loader"]
    K --> G{"Execution evidence complete?"}
    G -->|No| H["Hold with exact missing evidence or access"]
    H --> K
    G -->|Yes| P["M4b: bounded Choi descriptive run"]
    P --> R["M5: reviewed evidence package and Ravel PR"]
    R --> U["M6: unseen-paper qualification"]
    U --> A["Separately activate bounded recurring operation"]
    B --> E["M1 / M2: correction, coverage and independent screening evaluation"]
    E --> U
```

Future arrows are not implemented enforcement. The [cloud runbook](CLOUD_SETUP.md)
is the next handoff; [environment qualification](EXECUTION_ENVIRONMENT.md) owns
resource requirements. Setup can pass while scientific execution remains held.

## State and artifacts to implement in M3

Use one coordinator-owned ledger, initially SQLite with serialized writes and
append-only events/attempts. The dot cloud computer is a candidate host, subject
to proving executable access, persistence and recovery. Dot memory and independent
SQLite copies in every task are not the ledger. If that host fails qualification,
report the specific gap before selecting another cloud service. No always-on
local machine is part of this design.

Workers receive immutable packets: paper/version, RQ-context/policy hashes,
contract/code/input identifiers, attempt/lease IDs, output destination and limits.
A deterministic job key prevents duplicate logical jobs. Retries retain earlier
attempts; scientific parameter changes require an amendment and new key. An expired
lease with an unknown worker outcome holds redispatch until reconciled.

Workers return manifests, hashes, logs, QC and exit/cancellation/resource receipts.
Verify these before transitions. Export required artifacts before marking a job
complete and test restoration outside the original task. Compact public receipts
may enter Git. Full texts, private preferences, SQLite state and large outputs
need appropriately permissioned storage outside public Git. Qualify the initial
artifact destination before M4; no paid store is implicitly selected.

## Usage and failure policy

Start with one manually dispatched cloud task, without a recurring responsibility.
The product route uses the signed-in account; current standard-library Weft
commands need no OpenAI API key. Record observable Work/Codex usage or mark it
unavailable; do not convert account percentages to invented dollar charges.
Existing `model_usd_*` fields are inactive API-route proposals, not enforceable
subscription caps. M3 must implement/review a product-route budget representation
before unattended dispatch.

The one-job, six-hour and 20-GiB download proposals in `configs/policy.json` are
ceilings to qualify, not OpenAI runtime guarantees. Use the smaller of approved
workload limits and measured platform limits. If memory/time/process cancellation
cannot be enforced, hold science and identify the missing control. Text instructions
are not resource limiters. Unknown outcomes, drift, interrupted export and usage
exhaustion retain resumable holds/attempts; do not retry blindly.

## Next code slice

Implemented: `weft/` discovery/context/buffer/reading/validation; `configs/`;
`integration/ravel.lock.json`; `tests/`; compact `records/`.
Add job ledger, executor, coordinator handoff and exporter modules when functional.
Next: immutable job/attempt/lease/receipt schemas, a single-writer ledger, synthetic
executor and duplicate/unknown-outcome tests; qualify cloud capabilities alongside.
Numeric dependencies and Ravel analysis code belong to M4a after scope review.
No automatic acceptance, merge, RQ registration, paid fallback or schedule follows
from environment setup.
