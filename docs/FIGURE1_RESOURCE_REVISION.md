# Figure1 resource revision proposal — 11 October 2026

**Decision pending; not applied.** The current Figure1 job has not started.
[Preparation evidence](../records/choi-figure1-preparation-20261011.json) records
the stopped source clone and preserved reservation.

The frozen plan allocates 16 GiB to the analysis and requires 20 GiB available on
the host. The current worker reports only 17.59 GiB total host memory and a visible
16 GiB cgroup limit. Its precise relation to Docker and any ancestor limits is
unverified. Waiting for 20 GiB availability is not a sound plan for this worker.
The earlier environment-capacity observation is not a guarantee for this task.

| Option | Concrete change | Qualification and limitation |
| --- | --- | --- |
| Bounded 8 GiB pilot (recommended) | New operational resource amendment: 4 CPUs, 8 GiB memory/no additional swap, 12 GiB host-availability floor, same 3,600-second watchdog and 512 MiB tmpfs | Recheck effective cgroup/Docker limits and capacity, inspect actual container controls, reuse verified source/inputs, and make a new verified before-dispatch checkpoint for the existing unstarted reservation. Metadata used ~924 MiB and the same 8 GiB cap successfully; full Figure1 memory is unknown. OOM/deadline ends the attempt and preserves failure; no automatic rescue. |
| Qualify a larger cloud worker | Keep 16 GiB analysis and 20 GiB host floor | Establish actual task capacity and restore source/runtime/inputs/checkpoints in a new qualified worker first. Availability, provider controls and any extra cost are unconfirmed; no new service or spend is authorized. |

The 8 GiB option reduces the container ceiling while retaining 4 GiB of planned
host headroom. It does not change cell QC, marker rules, clustering, estimands,
output format, network isolation, scientific acceptance or retry policy.
The sparse-loader measurement supports trying a bounded workload; it does not
prove the full workload will fit.

After the owner's choice, preserve frozen v1 files and add an explicit immutable
operational amendment to the new packet. Reconcile the authoritative ledger and
held reservation before any preparation resumes. No additional numerical attempt
exists yet; no old metadata analysis is rerun. Actual figure dispatch still needs
a complete reviewed packet, input/source/control checks and verified checkpoint.
