# W08 runtime and author-code qualification

Status, 21 October 2026: **live execution held; local preparation advanced**.
The critical dependency is a supported current runtime observation on the
existing held native child, followed by qualification of the new author worker.
Fixing capability exposure alone does not finish the scientific adapter or W08.

Follow-through: the owner authorized private support submission; the request and
minimal addendum were submitted and human escalation was confirmed on 21 October.
No ticket number was displayed. Replies are expected in that support conversation
and by email. The [worker integration preparation](AUTHOR_WORKER_INTEGRATION.md)
and [R01 contract draft](../proposals/R01_PILOT_CONTRACT_20261021.md) advance independent
work while the platform response is pending. Neither is live qualification.

## What is already evidenced

- The original native launch was admitted. Its latest completed report still
  states that no runtime-status capability was exposed and zero tests ran.
  Read-only retrieval on 21 October confirmed that saved report; it did not ask
  the child to run another diagnostic or establish its current runtime state.
- [Earlier manual container evidence](../../records/cloud-runtime-20261011.json)
  records non-root execution, dropped capabilities, no new privileges, read-only
  root, network isolation, memory/PID failure and descendant cancellation. This
  is historical synthetic evidence from another task/configuration, whose original
  overall HOLD remains preserved. It is a reusable test design, not fresh authority.
- [The Weft adapter](../SCIENTIFIC_ADAPTER.md) handles immutable packages and
  controlled fixture recovery. It has no live author-code dispatcher. The old
  Docker executor intentionally accepts only its built-in synthetic fixture.

## Required evidence and next work

| Requirement | Concrete check | Current state |
|---|---|---|
| Correct current runtime | Supported runtime response binds actual task, environment/configuration version and policy; `observations_current=true`, network state `enforced` | Platform capability absent in the last child report; needs operator repair/equivalent |
| Original occurrence identity | Reconcile retained submission, task/turn acknowledgement and delivered prompt representation, including final LF | No documented normalization/raw delivery proof yet; retain original hashes |
| Frozen worker package | Exact Weft package, code/environment/image hashes, approved argv, read-only staged inputs/code and fresh outputs | Package machinery exists; real author-worker dispatcher still needs integration |
| No credential or host access | Explicit safe environment allowlist; no injected proxy credentials, host home, Docker socket, devices, shared namespaces or arbitrary mounts | New offline auditor checks supplied observations; live trusted observation pending |
| Enforced resource limits | Actual cgroup CPU/memory/swap/PIDs, bounded scratch and output-volume quota, with small bounded failure probes | Historical synthetic controls exist; fresh route/output-quota qualification pending |
| Reliable termination | External watchdog remains effective if coordinator disconnects; timeout/cancel kills descendants, observed outside author code | Existing cooperative expiry correctly holds unknown; surviving watchdog not implemented/qualified |
| Recoverable outputs | Bind exact run/attempt, collect after verified termination, save private receipt/output hashes, independently restore; unknown means no retry | Fixture recovery exists; real output/worker binding and fresh restore demonstration pending |
| Scientific readiness | Inspect real inputs and units; freeze exact comparison, endpoint, methods, limitations, code/stack and finite resource budget | R01 remains a candidate with metadata-only feasibility; no real W08 contract frozen |

## Read-only control auditor

[author_isolation.py](../../weft/author_isolation.py) audits supplied Docker inspect
JSON plus a trusted pre-author probe against a separately hashed plan. It has no
Docker/subprocess/network call and grants no dispatch authority. Its
[portable tests](../../tests/test_author_isolation.py) can run on Windows without
pretending to test Linux enforcement:

```powershell
python -m unittest discover -s tests -p test_author_isolation.py -q
python -m weft.author_isolation --plan private/plan.json --expected-plan-sha256 <retained-hash> --inspect private/inspect.json --probe private/probe.json
```

Plan fields: `schema_version: weft-author-isolation-v1`, container ID/name,
digest-pinned image and platform image ID, frozen argv, exact allowed environment,
separate staged `/code`, `/inputs`, `/outputs` mounts, memory/PID/CPU and scratch
bounds. Container inspection must match the plan and restrict privileges,
namespaces, devices, restart policy, network, mounts and writable paths. The probe
records actual UID/GID, capabilities, syscall restriction, cgroups, interfaces,
denied code/input/root writes and absence of a host socket/canary. Never read real
credentials to create a canary; use deliberately nonsecret test data.

Even `supplied-controls-consistent` explicitly returns `runtime_qualified=false`
and `dispatch_authorized=false`. Hashes do not authenticate observations; the
trusted worker must capture them before running author code. The auditor does
not establish kernel output quota, surviving watchdog, process termination or
external restoration. Those require actual worker-side implementation/probes.
No new command is wired into scientific preflight as a bypass.

## Practical execution sequence after platform repair

1. Read the supported current runtime status on the preserved occurrence and
   verify identity, policy/version and current enforcement. Resolve prompt binding
   with platform evidence; do not silently normalize the frozen expected hash.
2. Finish the separate author dispatcher using the supported worker controls.
   Keep downloads/builds in trusted preparation; execute author code without
   network/credentials. Pin the image, package, input mount manifest and argv.
3. Qualify a **new, explicitly scoped author-isolation test occurrence** using
   trusted canaries only: readable inputs, denied writes/host access, permitted
   outputs, bounded resource exhaustion, timeout/cancel/disconnect and recovery.
   The old native fixture occurrence keeps its original scope. A replacement or
   changed gate requires explicit review, not an automatic retry.
4. Inspect R01's actual files under bounded preparation, then produce the concrete
   real-data contract. The logged candidate is GSE303805: five deposited samples,
   each labelled rep1, with pooled eyes reported in the retained Methods. Those
   are prior metadata findings, not a new inspection or independent replication.
   The candidate question remains robustness of regenerated epithelial-cell
   resemblance to uninjured limbal cells under defensible QC/annotation/integration
   choices. Do not invent thresholds, individual donor IDs or a causal endpoint.
5. Present the resulting one-page contract with exact data, methods and measured
   limits for the owner's consequential scientific decisions. After that and
   passing worker qualification, run once, retain failures/nulls, recover outputs
   and complete QC/critique and owner disposition.

The owner does not need to design Docker flags or acquire another computer.
The [focused support request](../support/W08_RUNTIME_REQUEST_20261021.md) is now
submitted. The next owner action is to return the specialist response here when
it arrives; no further permission or resubmission is needed now. Later approval should concern
the concrete pilot contract and any platform-required change, not unspecified
permissions or invented scientific thresholds. W11 remote autonomy and W12
recurrence remain separate from a manually supervised W08 pilot.

## Source basis

The installed managed-cloud runtime skill version 0.1.2 names the status operation
and current/enforced observation requirements. No matching operation was exposed
in this desktop session's tool inventory either; that is not a fresh inspection
of the child's tools. [Official environment documentation](https://learn.chatgpt.com/docs/environments/cloud-environments)
distinguishes editable setup from each task's retained state. The
[sandbox security guidance](https://developers.openai.com/api/docs/guides/agents-api/environments/security)
explains why code can access whatever files/credentials/network its environment
exposes; it is general guidance, not proof of capabilities on the selected Work
task and not a recommendation to switch to the paid Agents API.
