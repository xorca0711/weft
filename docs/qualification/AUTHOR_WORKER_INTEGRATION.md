# Author worker integration preparation

25 October 2026. **Offline preparation, reservations and transfer implemented;
live dispatch held.**
This is the bridge between the immutable scientific package and a future trusted
worker. It does not change the frozen native occurrence or the synthetic executor.

## Implemented interface

[author_worker.py](../../weft/author_worker.py) revalidates the entire scientific
package and retains a content-addressed proposal in private
`worker-preparations/<sha256>.json`. It carries only the actual code and data
inventory needed for `/code` and `/inputs`; papers, reviews and host bindings are
not automatically mounted. File references retain exact bytes/hashes and resolve
under the existing registered roots. Case-insensitive and file/directory destination
collisions fail. Source/code/contract or worker implementation drift invalidates
reuse. No files are uploaded or copied into a live worker.

```powershell
python -m weft.author_worker --root <private-workspace> --package-reference <package-ref.json> --request <worker-request.json>
```

The request has exactly `image`, `image_id`, `argv`, `environment`, `pids`,
`nano_cpus`, `tmpfs_bytes` and `output_bytes`. Image digest, platform image ID,
safe environment and explicit reference to frozen code are required. Memory,
wall time, disk, attempt and spending bounds come from the contract. Frozen
staging bytes plus output and scratch must fit its disk bound; scratch must leave
memory for the process. Live logs, shared memory and transfer overhead still need
their own measured allocation within the same bound.
These checks compare proposed bounds, not measured feasibility or enforcement.
Exit zero means preparation saved; `dispatch_authorized` remains false.

`observation_plan(workspace, preparation_ref, assignment)` produces the separate
isolation auditor's exact expected plan. Assignment fields are `job_id`,
`attempt_id`, `container_id`, `staging_root`. The proposed name and isolated
staging subdirectory bind preparation/job/attempt/root; the daemon-assigned
container ID is added for inspection. Every use revalidates the package.
`inspect_supplied(...)` feeds that plan to the existing auditor and explicitly
keeps assignment authentication, output quota, watchdog and dispatch false.
There is no reservation, launch, cancellation or terminal ledger update here.

## Concrete live integration contract

The local preparation lifecycle is now implemented in
[author_attempts.py](../../weft/author_attempts.py). `open_attempts(workspace)` uses
the authoritative `control/jobs.sqlite` and existing global slot. `reserve(ref)`
pins the preparation and lifecycle implementation, writes an exclusive private
checkpoint and consumes the frozen attempt budget. It provides no start API.
`status(claim)` does not expose the lease token. A pristine, unexpired preparation
can be abandoned; expiry, cancellation or supplied worker observations retain the
slot. `observe(claim, report)` stores bounded immutable evidence and sets unknown,
even if the report claims success. Legacy synthetic reconciliation/binding rejects
this packet kind. Recovery remains readable after input drift; new admission does
not. An orphaned checkpoint is retained and prevents silent attempt-ID reuse.

[author_transfer.py](../../weft/author_transfer.py) provides `stage`, `collect`
and independent `verify` functions with explicit file/entry/per-file/total-byte
bounds. Staging copies only frozen code/data as inert bytes to a separate root.
Collection accepts only contract output names, preserves missing outputs and
retains failures. Files stream in bounded chunks and are checked for exact size,
hash, identity and modification during transfer. Links, special files, traversal,
case/prefix collisions and extra files/directories fail. Exact complete copies
resume; partial copies stay held and are never overwritten. A changed input size
is rejected before hashing, and frozen-reference hashing reads at most its size
plus one byte. This changes the evidence-module implementation pin; historical
packages are preserved and require a new package for current-code admission.

The collector writes its immutable manifest after copying and independently
verifies it. This is a **quarantined return**, not a termination receipt: identity
authentication, termination and dispatch remain false; it cannot release a slot.
Use these functions only on trusted quiescent directories. They are not a sandbox
against concurrent hostile filesystem mutation. No archive extraction, upload,
live mounts, quota or daemon operations are implemented by this local transport.
The real backend must establish quiescence and reverify copies before use.

The [qualification campaign](AUTHOR_QUALIFICATION_CAMPAIGN.md) supplies a bounded
trusted canary and twelve-scenario protocol. [R01 preparation](../proposals/R01_IMPLEMENTATION_PREPARATION.md)
supplies tested calculation mechanics and the remaining scientific freeze gates.
Validation is recorded [here](../../records/technical-preparation-validation-20261025.json).

| Step / owner | Required behavior | Evidence before proceeding |
|---|---|---|
| Coordinator / Weft | Reserve an immutable author attempt in the existing `jobs/attempts/events` ledger and shared slot; new packet kind with separate admission | Authenticated reservation/checkpoint, exact package and preparation hashes; old synthetic and fixture APIs reject this kind |
| Platform / trusted worker | Obtain supported current runtime identity, configuration/version, policy enforcement and provenance | Current response bound to this task; old saved policy and bot prose cannot substitute |
| Trusted stager | Transfer only frozen inventory into fresh attempt paths; stream hash verification; reject links, devices, path escapes, extra files and mismatched bytes | Independent exact inventory, ownership/read-only mounts, no original research directory mounted; bounded decompression before admission |
| Trusted supervisor | Create output filesystem with kernel-enforced byte and inode bounds; arm independently supervised wall deadline before author start | Actual mount/quota evidence and bounded ENOSPC/inode probe; supervisor survives coordinator disconnect and has exact container/cgroup identity |
| Trusted worker | Create stopped container; clear inherited entrypoint, healthchecks and unsafe image environment; inspect all actual configuration | Exact digest/platform image, non-root, no credentials/proxy/socket/extra mounts, restricted namespaces/capabilities/syscalls, no network, limits |
| Trusted probe controller | Probe an otherwise matching disposable canary container before author execution; inspect actual author container too | Trusted observations; no author-provided control attestations; probe-to-author image/config equivalence recorded |
| Trusted supervisor | Start once only after all gates; cancel/timeout kills the complete bound process tree | Outside observation of container/cgroup emptiness, including descendants; no completion inferred from a lease expiring |
| Collector / Weft | Read outputs only after verified termination; bound file count, bytes, paths and types; hash and save receipt before terminal application | Attempt/package identity, exit reason, stdout/stderr and failures retained, receipt/output restore independently demonstrated |

An unacknowledged start, lost supervisor, missing termination proof or incomplete
receipt becomes **unknown with the slot reserved**. Recovery reconciles the same
attempt; it cannot redispatch it. No daemon cleanup by name prefix or unrelated
container deletion is allowed. Do not extend `FixtureReplay` to accept real data
or weaken the old synthetic executor; the live packet requires its own reviewed
adapter and evidence producer.

## Choices resolved for preparation

- Use a separate trusted supervisor outside the author container. A Python
  timeout in the coordinator is insufficient after the coordinator dies. Do not
  implement a guessed provider supervisor; bind the supported service once the
  platform response identifies it. No new service/privilege is installed here.
- Require an actual output-volume quota, including inode limits. The transport
  manifest byte limit and a read-only container root do not bound a writable bind
  mount. The platform must expose a suitable quota-backed volume or equivalent
  enforced storage route; no privileged loop mount is introduced as a workaround.
- Build/download dependencies during trusted preparation, then execute author
  code offline. Review and clean image environment defaults; do not expand the
  allowlist merely because a base image injects extra variables. Disable image
  healthchecks so they cannot run unreviewed commands outside the frozen argv;
  the supplied-observation auditor now rejects enabled or malformed healthchecks.
  Include `/dev/shm`, container logs and preparation/transfer buffers in the live
  storage/memory inventory; bounding `/tmp` alone is not complete quota evidence.
- Preserve large input streaming. Existing input hashes support files above
  1 MiB, while structured records are bounded. The fixture return's 1 MiB/file,
  8 MiB total bounds remain fixture bounds. A real collector needs a separately
  bounded streaming artifact route for figures/tables/logs; no silent relaxation.
- Qualification is a new, narrowly scoped occurrence using trusted canaries.
  It must test success, failure, timeout, cancellation, coordinator loss, memory/
  PID/output/inode exhaustion, stale identity and restart/recovery. It cannot be
  appended to the original frozen native test command.

Docker documents that resource constraints depend on kernel support and must be
configured explicitly; image defaults include environment and entrypoint behavior.
See [resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)
and [container execution](https://docs.docker.com/engine/containers/run/).
These documents guide the design; they do not establish capabilities on the held
cloud task. The [W08 unblock plan](W08_RUNTIME_UNBLOCK.md) owns platform gates;
the [R01 contract draft](../proposals/R01_PILOT_CONTRACT_20261021.md) owns scientific scope.
