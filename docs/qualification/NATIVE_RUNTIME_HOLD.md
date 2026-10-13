# Native launch admitted; runtime preflight held

**13 October 2026 — L1 partial, execution held.** This is the outcome of the
[frozen native trial](NATIVE_SYNTHETIC_TRIAL.md), not a new occurrence.

| Check | Evidence and result |
|---|---|
| Native admission | Owner-relayed Mir report records one create call and real task/turn acknowledgement. Root directly reads the resulting child, whose delegation identifies the original coordinator |
| Intent journal | Mir reports prepared → awaiting acknowledgement → acknowledged, with matching reopen checks. Root has not independently read that coordinator database |
| Exact prompt binding | Root observes one missing terminal LF in child text. Mir's owner-relayed comparison finds the saved prompt and retained create argument both match the frozen 4,673 bytes; child text is 4,672 bytes. No raw wire capture; normalization layer unknown |
| Child outcome | Root directly observes an idle task, completed turn and preflight HOLD; no source retrieval or test invocation |
| Artifact recovery | Root decodes and verifies the original 3,165-byte receipt and empty test log against the reported SHA-256 hashes. Mir separately reports identical completed-task readback |
| Policy snapshot | Child reports a restricted policy file with the three custom hosts. Its SHA-256 exactly matches the earlier manual worker's saved snapshot; that does not establish current enforcement or version |
| Execution/isolation | Zero test invocations. Timeout, isolation and the 12-fixture result remain untested in this child |

The original preflight could not locate managed-cloud instructions or a supported
current configuration/policy-status interface. A single same-child diagnostic
then completed. Root directly read its final report: the child inspected 341
operations, all three cloud skill pages (55 skills) and the empty executor skill
catalog. It reports no runtime-status operation, runtime skill or supported lazy
tool discovery. Status calls/retries were 0/0, with no explicit access denial.

This establishes reported absence within the inspected catalogs; root retrieved
the completed diagnostic report, not the raw catalogs. Deployment, routing and
permission causes remain indistinguishable. Current enforcement and configuration
version remain unknown. The task metadata still showed active at root's read,
while the specific diagnostic turn was completed; no new work was inferred from
that metadata discrepancy.

The root's installed `cloud-environment-runtime` skill, version 0.1.2, specifies
`cloud_environment.environment_status` and requires current observations with
network state `enforced`. The root's tool catalog does not expose that operation;
reading its local skill cannot add it to this child. A plugin-directory search
returned no matching runtime plugin; unrelated hosting plugins were not selected.
The directory result is not proof that this built-in capability is unavailable
on every surface.

The established blocker is **missing runtime capability exposure in the child's
reported catalogs**. Its cause is unknown; an unpublished environment or incorrect
allowlist has not been demonstrated.
The successful native admission and identical policy-file hash narrow the problem;
they do not satisfy the frozen enforcement gate. The
[official environment guide](https://learn.chatgpt.com/docs/environments/cloud-environments)
documents configured network settings and task creation, but does not establish
which status tool this particular child receives.

## Diagnosis complete; platform review next

The owner sent exactly one capability-only follow-up to the existing child. Do
not resend `MIR_SAME_CHILD_DIAGNOSTIC.txt` or the original launch prompt. No test,
source fetch, installation, policy change, export or replacement task followed.

Mir's owner-relayed byte comparison places the earliest observed discrepancy
between the retained create argument and the decoded child-input representation:
only the final LF at offset 4672 is absent. Both saved prompt and retained argument
hash to the original frozen hash. A raw serialized request was not retained;
which submission/storage/readback layer transformed the representation is unknown.
Original spec, journal, prompt and HOLD artifacts remain preserved. The retained
receipt hash was rechecked by Mir; exact delivered-byte binding remains unqualified.

The [support request](../support/LAUNCHER_SUPPORT_REQUEST_20261013.md) now asks the
platform operator to inspect runtime integration exposure on this existing task
and document prompt normalization. A private task/turn-ID addendum is ready under
ignored run records. Neither the request nor the addendum has been sent by root.
No further diagnostic turn or new occurrence is justified without new evidence.
A repair requiring access changes, republishing or a replacement worker needs
separate review. Keep the original execution gate unchanged.

Raw child reads, decoded artifacts, root verification and attributed Mir reports
remain private. Roadmap: **L1 partial; execution held for platform integration
review**. Choi stays closed, B4 held, and M6 disabled. No runtime or scientific
qualification follows from native admission and recovered HOLD evidence.
