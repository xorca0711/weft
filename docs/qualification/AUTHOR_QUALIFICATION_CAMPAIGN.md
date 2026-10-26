# Author worker qualification campaign

25 October 2026. Payload and protocol prepared; **no live campaign executed**.
Use a new authorized occurrence after current runtime identity/policy and a
supported supervisor/quota route are established. Never extend the original
frozen native command or rerun the held child implicitly.

The project-owned [canary](../../weft/author_canary.py) defaults to printing a plan:

```powershell
python -m weft.author_canary output
```

`--execute` is for the disposable isolated worker after admission. Modes are
success, failure, sleep, descendants, memory, pids, output and inodes. Allocation
is capped at 64 MiB, spawned children at eight, writes at 8 MiB and created files
at 256. Sleep/descendant payloads wait 15 seconds. An external watchdog must
bound stalled I/O and total runtime. Payload output never proves enforcement.
Local tests run success, failure and simulated ENOSPC only, without host exhaustion.

For live exhaustion tests, set a disposable container's verified quota below the
payload cap and above measured startup needs. Freeze exact limits before each
attempt. Count interpreter overhead, `/dev/shm`, logs, scratch, staging and
transfer buffers. If supported limits cannot fit these caps, stop and revise the
campaign; do not raise privileges or substitute a privileged loop mount. Each
scenario has one attempt, with no automatic retry.

| Scenario | Required outside observation |
|---|---|
| Success / explicit failure | Bound container, exit code, complete/failed inventory and immutable receipt |
| Timeout / cancellation | Supervisor armed before start; whole bound cgroup empty after termination |
| Coordinator loss | Independent deadline still fires; coordinator reconciles the same attempt |
| Memory / PID limits | Effective kernel/cgroup settings and independently observed enforcement |
| Output byte / inode limits | Kernel quota/mount identity, ENOSPC/inode event and actual bounded usage |
| Stale identity | Wrong task, image, container, attempt or policy rejected before start |
| Restart / unknown result | Shared slot retained; zero duplicate starts; same-attempt recovery |
| Independent restore | Receipt and every artifact hash verified from a separate private copy |

All twelve scenario names are enumerated in `author_canary.CAMPAIGN`. The future
provider controller must retain source hashes, approved campaign, current runtime
response, task/container/cgroup identity, package/preparation hashes, timestamps,
outside observations, control settings, termination evidence and output hashes.
Probe image/configuration must match the author container except its trusted
command; inspect the stopped author container separately. Caller JSON, a lease
token, a restored manifest or an "all passed" boolean cannot authenticate these
observations or enable dispatch.

The missing implementation is the concrete provider controller for authenticated
admission, quota creation, supervised start/cancel and outside termination
reconciliation. Its API cannot be inferred from Docker syntax or an installed
skill. [Worker integration](AUTHOR_WORKER_INTEGRATION.md) and
[runtime unblock](W08_RUNTIME_UNBLOCK.md) retain this boundary.
