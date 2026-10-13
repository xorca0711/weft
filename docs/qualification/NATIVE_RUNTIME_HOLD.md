# Native launch admitted; runtime preflight held

**13 October 2026 — L1 partial, execution held.** This is the outcome of the
[frozen native trial](NATIVE_SYNTHETIC_TRIAL.md), not a new occurrence.

| Check | Evidence and result |
|---|---|
| Native admission | Owner-relayed Mir report records one create call and real task/turn acknowledgement. Root directly reads the resulting child, whose delegation identifies the original coordinator |
| Intent journal | Mir reports prepared → awaiting acknowledgement → acknowledged, with matching reopen checks. Root has not independently read that coordinator database |
| Exact prompt binding | Root's child transcript matches the frozen text except for one absent terminal LF. The original call arguments have not been inspected; the normalization layer is unknown |
| Child outcome | Root directly observes an idle task, completed turn and preflight HOLD; no source retrieval or test invocation |
| Artifact recovery | Root decodes and verifies the original 3,165-byte receipt and empty test log against the reported SHA-256 hashes. Mir separately reports identical completed-task readback |
| Policy snapshot | Child reports a restricted policy file with the three custom hosts. Its SHA-256 exactly matches the earlier manual worker's saved snapshot; that does not establish current enforcement or version |
| Execution/isolation | Zero test invocations. Timeout, isolation and the 12-fixture result remain untested in this child |

The worker could not locate managed-cloud instructions or a supported current
configuration/policy-status interface. Its trace contains filesystem discovery
and MCP resource/template listing, but no runtime-status call. That does not
establish whether a tool was absent, undiscovered or omitted from this session's
runtime integration. Do not diagnose an installation defect from that trace alone.

The root's installed `cloud-environment-runtime` skill, version 0.1.2, specifies
`cloud_environment.environment_status` and requires current observations with
network state `enforced`. The root's tool catalog does not expose that operation;
reading its local skill cannot add it to this child. A plugin-directory search
returned no matching runtime plugin; unrelated hosting plugins were not selected.
The directory result is not proof that this built-in capability is unavailable
on every surface.

The likely failure class is **runtime capability exposure/discovery**, not a
demonstrated unpublished environment or incorrect allowlist. This is an inference.
The successful native admission and identical policy-file hash narrow the problem;
they do not satisfy the frozen enforcement gate. The
[official environment guide](https://learn.chatgpt.com/docs/environments/cloud-environments)
documents configured network settings and task creation, but does not establish
which status tool this particular child receives.

## Next bounded diagnosis

A private, unsent Mir handoff is prepared beside the original dispatch packet:
`MIR_SAME_CHILD_DIAGNOSTIC.txt`. It requests one capability-only follow-up to the
**existing child**, plus read-only inspection of Mir's retained submission bytes.
It grants no test execution, source retrieval, replacement task, installation,
policy change, Drive export, ledger mutation or scientific work.

1. Inspect the actual child skill/tool catalog and any supported lazy tool
   discovery. Filesystem searches and MCP resource lists alone are not a complete
   tool catalog. Identify the runtime skill/status tool if actually exposed.
2. If that supported tool exists and permits this task, read its current status
   once. Otherwise report the exact missing capability; do not invent endpoints,
   import another session's tools, or copy a skill to manufacture access.
3. Compare retained coordinator prompt/call bytes with the frozen prompt and
   the child transcript's text. Preserve all original bytes/hashes. Do not silently
   canonicalize or change the original journal. Formatting equivalence is not an
   exact-byte pass; a normalization contract would be a reviewed amendment.
4. Keep tests held even if the diagnosis succeeds. Review any supported repair or
   same-task continuation before executing the original unstarted fixture run.

If the runtime integration is unavailable, the prepared
[support request](../support/LAUNCHER_SUPPORT_REQUEST_20261013.md) asks how to expose
it on the existing task. A repair requiring access changes, republishing or a new
worker is a separate decision. No such action has been taken.

Raw child reads, decoded artifacts, root verification and the attributed Mir
relay are stored under ignored private run records. Choi remains closed, B4 held,
and M6 disabled. Native admission/recovery is progress; L1 is not complete.
