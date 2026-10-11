# Current project state

**Update this before stopping work, every session.**

## Cloud setup in progress; synthetic job controls — 11 October 2026

The owner authorized UI setup at PR #1 revision
`d031cef02ab4a417760bca46e90a63917d215d31`, setup checks, publication on success
and subsequent progress toward Choi. That setup baseline remains unchanged.
Follow-up implementation is isolated on `codex/cloud-job-controls-20261011`.

Browser sign-in completed, but the visible account reported **Free** and the
Codex Cloud link redirected to ChatGPT home. This differs from the previously
confirmed environment-creation access. The owner was asked to switch to the
account/workspace with cloud access; the answer remains pending. No upgrade,
account modification, environment, cloud task or numerical analysis was started.
No private account identifier is included in this public record.

Meanwhile, implemented [synthetic job controls](docs/JOB_CONTROLS.md): stable packet
identity, input hashes, transactional single-slot claiming, append-only transitions,
unknown-outcome holds, cancellation requests and bounded retries. Fourteen targeted
tests passed, including competing database connections and restart after expiry.
The full suite now passes **72 tests**; offline validation also passes.
This is a library foundation, not a qualified executor or complete M3 gate engine.
Terminal reports remain explicitly self-reported; success/analysis dispatch is absent.

Next: complete cloud setup after account access resolves, retaining d031cef for
initial checks; then qualify actual runtime/artifact capabilities before integrating
this follow-up code. Add verified executor receipts, artifact export/restore and
hard runtime controls before any scientific contract can be dispatched. Existing
policy flags, Ravel pin and historical evidence remain unchanged.

## Dot + Codex Cloud roadmap — 11 October 2026

Work remains on `codex/discovery-review-buffer-20261011` in
[PR #1](https://github.com/xorca0711/weft/pull/1). The refreshed main base is
`59aa0f740b8e3d6d856684ef7052f5e7d77b7820`; the read-only Ravel pin remains
`bfe26b876221cf6c6fa6f9b16a90cfb516b5998d`. Ravel files/evidence are unchanged.
The PR contains discovery/reader and source-audit work; cloud setup must select its
reviewed full revision instead of assuming main already contains it.

The owner selected **dot coordination and Codex Cloud execution**, with no extra
local PC, and confirmed Create environment plus Weft repository availability.
No published/qualified environment or dot assignment is confirmed. The
[roadmap](docs/IMPLEMENTATION_PLAN.md), README diagram,
[environment specification](docs/EXECUTION_ENVIRONMENT.md), pilot metadata and
agent handoff reflect this choice. The [cloud runbook](docs/CLOUD_SETUP.md) provides
owner access actions, the setup brief and required qualification receipts.
The former 32-GiB separate-host proposal is superseded; actual cloud resources
and scientific peak memory/runtime remain unknown.

Completed baseline: bounded Europe PMC discovery/dedup, pinned RQ context,
proposal buffer, manual XML reader and Choi main-figure/S1-S7/input audit.
See [source review](docs/PILOT_CHOI_REVIEW.md),
[review receipt](records/pilot-review-20261011.json),
[input inventory](records/pilot-inputs-20261011.json) and
[prior validation](records/pilot-review-validation-20261011.json).
These frozen records and the original reading assessment remain preserved.
Initial profiles cover A0/A1; context supports all 32 RQs. M1 correction/version/
recall and M2 independent screening evaluation remain unfinished.

No cloud task, numerical run, Ravel contract, scientific acceptance, paid fallback
or schedule was activated. Validators and scientific gate semantics are unchanged;
all policy activation flags remain false. First-stage setup needs Python/Git,
not scientific packages, new API secrets or access to the local research drive.

## Exact next steps and external dependencies

1. Owner prepares private `weft-pilot` from the reviewed PR revision using the
   runbook. Review setup checks, publish and return the environment name/ID and
   report/task link. Account/repository visibility is already confirmed; do not
   request it again. Environment publication and qualification remain pending.
2. Implement M3 job/attempt/lease, immutable references, cancellation, hard limits,
   unknown-outcome reconciliation and artifact export/restore. Start with synthetic
   tests; development can continue alongside cloud setup. Per-task SQLite copies
   are not shared authoritative state.
3. Qualify one manual delegation through the selected existing dot after M3 controls
   exist. Verify cloud dispatch/return, ledger recovery and artifact retention without
   an awake desktop. Select another service only for a demonstrated capability gap.
4. Prepare/review the Ravel contract and dependency lock. Qualify public input
   transfer, coordinates/values, sparse memory, enforced limits and comparison
   criteria. Preserve known outcome exposure and published/adapted differences.
5. Run P001 only when readiness passes, then propose reviewed Ravel integration.
   No pAT2 call or no new RQ is legitimate. Qualify unseen papers and complete
   screening/correction evaluation before recurring activation.

This session has no verified cloud-environment inventory/provisioning tool; local
project enumeration cannot establish cloud access. Owner confirmation establishes
UI availability only. Additional artifact storage/access is a conditional future
request, not a service already selected or a blocker to initial setup.

Validation for this slice: **58 unit tests passed**, offline validation passed,
all **66 root/docs local links** resolved and `git diff --check` passed. The source
records, Ravel pin, scientific policy and validator/code files are unchanged.
No biological rerun is needed. Prior audit files remain ignored in
`runs/pilot-review-20261011-v1` on X:; cloud tasks retrieve inputs explicitly.
