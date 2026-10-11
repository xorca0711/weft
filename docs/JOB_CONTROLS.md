# Synthetic job controls

The published environment baseline remains PR #1 revision
`d031cef02ab4a417760bca46e90a63917d215d31`. Development is on PR #2;
select its reviewed exact revision explicitly. No environment configuration,
scientific policy, Ravel authority or schedule is activated by these modules.

## Ledger and trusted executor

`weft/jobs.py` coordinates cooperating clients of **one** SQLite database. Packets
bind immutable paper/context/policy/contract/executor identities and input hashes.
Transactional claims reserve one slot; events and packets are append-only/immutable.
Lease expiry and cancellation requests do not imply termination. Unknown attempts
retain the slot across database reopen, blocking retries and competing jobs.

`weft/executor.py` adds a standard-library local Docker adapter for **synthetic
qualification only**. It accepts exactly `fixture.txt` containing `synthetic fixture`
and three built-in modes: `success`, `failure` (exit 23), and `cancel` (a waiting
child/grandchild tree). There is no caller-supplied command, shell, author code,
scientific input adapter or success/acceptance path. `executor_sha256(mode, wall_seconds)`
binds fixture mode, wall bound, implementation files, worker and immutable image.
Use it in the existing version-1 synthetic packet's executor field before submit.

The adapter reserves an immutable job/attempt/container-name binding **before any
Docker operation**. It attaches the returned container ID once, stages and rechecks
read-only fixture bytes, and verifies Docker configuration and the worker's actual
cgroup controls. The only image is the previously qualified digest:

```text
python@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1
```

The qualified Linux amd64 image ID is also checked. `--pull never` forbids implicit
image replacement. The runtime-documented local socket is used with endpoint/context/
TLS selectors cleared, preserving Docker config/credentials. No socket is mounted.
Containers run as UID/GID 65534, with all capabilities dropped, no-new-privileges,
read-only root, one 16-MiB tmpfs, one read-only input mount, network none, 1 CPU,
256 MiB memory, no extra swap and 32 PIDs. Wall bounds are integers from 1–10 seconds.
A host monotonic deadline bounds start, inspect/top calls and execution; bounded
kill/wait and terminal reconciliation are separate operations. An interrupted or
unavailable host executor is not an independently surviving watchdog: lease expiry
holds that outcome rather than assuming the container stopped.

The adapter observes host PIDs and kernel start times, including descendants during
execution. Terminal reconciliation requires the exact bound Docker configuration,
`exited`, `Running=false`, PID 0, no Docker state error, and disappearance of every
observed process identity. A lingering zombie prevents verification. A timeout or
cancel request invokes bounded Docker kill/wait, then reobserves actual terminal
state; a client timeout alone never establishes cancellation. Missing containers,
failed daemon calls, absent snapshots, identity drift or surviving processes produce
`held_unknown`. Unknown containers are retained for recovery, not swept globally.
Only its own verified terminal container is removed; cleanup failure is reported
separately from verified termination.

`DockerExecutor.execute(ledger, claim, inputs_root=..., run_root=..., mode=...,
wall_seconds=...)` requires a fresh run directory. `recover` reobserves the same
container after expiry/restart using ledger-bound process evidence and exact code
identity. It does not accept a caller's claimed terminal hash as termination proof.
A crash before a sufficient process snapshot or loss of the container remains held.

All executor-bound attempts reject the legacy `reconcile` method, including after
expiry/reopen. That method remains available only for the original cooperative
ledger fixtures; its self-reported hashes cannot release real executor attempts.
Internal underscore methods are trusted adapter plumbing, not remote report APIs.
Python/SQLite/Docker administrator access is outside this cooperative threat model;
content hashes and triggers are not actor authentication or a hostile-client sandbox.

## Content verification and recovery

`weft/artifacts.py` emits canonical, strict terminal and output manifests binding
packet/input/code/image/job/attempt/container identities. Outputs are hashed from
actual bytes. Deterministic fixture output is checked against the built-in expected
result before recording `local_verified`. Failure/cancellation have no success
output. Unknown outcomes cannot produce a terminal manifest or release the slot.

The ledger stores the verified terminal content hash. Archive consumers must receive
that hash and expected identity through the trusted coordinator; an archive's own
claims, or an untrusted caller-provided hash, cannot supply the authority anchor.
`restore_archive` checks the expected archive hash, canonical JSON, terminal/manifest/
output hashes, exact members and identity, ZIP CRC and sizes **before** creating a
fresh restoration directory. It rejects duplicate/missing/unexpected members,
traversal, symlinks, special files, encrypted members, schema/type drift, expansion
over 2 MiB total or 1 MiB per member, and existing/symlink restoration paths. No
restored file executes. ZIP metadata/order are deterministic for identical content;
attempt/container identities intentionally differ between actual attempts.

## Implemented outcomes and remaining integration

A verified local success records `local_verified`, not whole-job completion or
scientific success. `failed` and `cancelled` record independently observed terminal
outcomes. `held_unknown` reserves the slot. Every returned terminal result explicitly
has `external_export_verified=false`. There is no API that marks a job complete
because someone claims an upload or supplies a checksum.

The existing connected **Google Drive product tools** are the qualified synthetic
transport. This adapter does not invent a Drive SDK, store credentials, create
sharing grants or publish artifacts. Integration still needs coordinator-owned
expected identities/hash anchors, upload-result reconciliation, private metadata
readback, raw-byte retrieval and checksum-verified restoration tied to the same
attempt. Prior independent cloud restore qualifies the demonstrated small route,
not arbitrary output size or retention guarantees. Private locators and raw runtime
logs stay outside public files.

One authoritative ledger location, backup/restore, actor authorization, product
usage budgeting, dot dispatch/return and unknown-outcome operational recovery remain
open. Independent task-local SQLite copies are separate ledgers, not distributed
coordination. All scientific contracts, numerical preflight and scientific gates
remain held.

## Validation

```bash
python -m unittest discover -s tests -q
python -m weft validate
```

The suite covers forged/tampered receipts, input/code/attempt/container drift,
unknown termination, expiry/restart, legacy reconciliation rejection, cancellation
requests, deterministic output/archive replay, bounded restoration and ZIP CRC.
Bounded actual adapter success and wall cancellation are additionally qualified
against the cached immutable image; they do not repeat the full runtime probe suite.
