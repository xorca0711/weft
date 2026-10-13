# One native synthetic launch through Mir

**13 October 2026 — submitted once; child preflight HOLD, zero tests.**
See the [verified outcome and next diagnosis](NATIVE_RUNTIME_HOLD.md).
The frozen specification below is preserved as the original trial scope.

The owner confirms that `weft-pilot` is selectable in the same-workspace Cloud
picker and has already been used repeatedly. Do not repeat that availability
check or manually create another worker to test native delegation. This is owner
attestation, not an independently retrieved AI-host account identity. The settings
screenshots and [interface reconciliation](NATIVE_LAUNCH_INTERFACE.md) remain the
configured-target evidence; the new runtime must verify its own enforcement.

The exact, self-contained handoff is saved privately under ignored
`runs/native-launch-qualification-20261013/dispatch-v1/`. The owner pastes
`MIR_NATIVE_SYNTHETIC_PROMPT.txt` into the **existing Mir chat**. It contains the
worker prompt, saved-environment identifiers, source pin and verification rules.
The owner relayed it to Mir, which reports one journaled native submission.
Root directly recovered the resulting child's HOLD artifacts. Do not paste the
launch prompt again; retain the original occurrence and use only the separately
prepared capability diagnostic for further review.

| Binding | Frozen scope |
|---|---|
| Occurrence | `weft-native-launch-20261013-v1` |
| Code | [PR #11](https://github.com/xorca0711/weft/pull/11), `824c562d5d0140aecadd35023fbaecca303ef126` |
| Fixture command | `PYTHONPATH=tests python -m unittest test_launches -q` |
| Expected outcome | 12 tests, no failures/errors/skips; one invocation |
| Bound | One native create call; 60-second source retrieval; 180-second enforced test deadline; at most 15 minutes of coordinator waiting before reporting pending |
| Result | Receipt and log, at most 64 KiB total raw bytes, returned through the same task and independently hash-verified |

Root reviewed the pinned offline journal, CLI integration and fixtures for this
cooperative synthetic scope. PR #11 remains open; both reported CI runs passed
at that exact head. Local runtime/test code is unchanged from the pin. Using it
for this qualification does not merge or deploy it, certify distributed ownership,
or change scientific gate semantics. No local runtime tests are repeated.

1. Mir checks for an existing occurrence, resolves the live exact saved target,
   preserves attributed identity/policy evidence and prepares the pinned journal.
2. Mir commits submission intent **before** one supported native creation call.
   Lost or ambiguous acknowledgement holds the occurrence; no replacement/retry.
3. The child checks actual version and enforced policy before source retrieval or
   tests. Unknown policy, drift, unavailable isolation or new access needs stop it.
4. Mir records the real task acknowledgement, recovers exact receipt/log bytes,
   and confirms identical readback from that completed task without another turn.

The journal's offline flags remain unchanged. Native submission is a separate
owner-authorized operation, and the fingerprints are evidence bindings rather
than authenticated service attestations. Only supported, available interfaces may
be used; denied browser operations and the unmapped CLI are not part of this trial.

After a successful result, reconcile L1 before planning L2 ownership and recovery
qualification. Same-task readback does not prove restart retention, provider
idempotency, PC-off continuity or cancellation. Choi stays closed, B4 stays held,
and M6 recurrence stays disabled. No Drive export or GitHub write is included.
