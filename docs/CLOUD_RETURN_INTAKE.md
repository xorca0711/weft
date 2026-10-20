# Offline cloud-result intake

The launch journal previously stopped at an acknowledged task. This extension
checks a supplied synthetic result bundle against that same task, its saved
launch specification and a separately frozen return contract. It reuses the
journal's state/history validation, existing local-file containment, portable
paths and material-size limits. It adds no provider adapter or cloud submission.

## Use and interpretation

```powershell
python -m weft launch-result-verify --journal private/launches.sqlite --operation <existing-occurrence> --contract private/return-contract.json --contract-sha256 <separately-retained-contract-hash> --directory private/returned-bundle --manifest-sha256 <separately-retained-manifest-hash>
```

The contract and manifest hashes are required. Keep them outside the copied
bundle before verification. A manifest supplied by a worker is not, by itself,
authenticated evidence. The JSON receipt format here is a **Weft normalization
contract**, not a claimed provider API. Preserve original raw observations with
the private run and document their transcription/limits; do not manufacture
missing runtime observations from requested settings.

Exit 0 means `consistent_synthetic_return`: the retained files, supplied
observations and expected fixture results agree within this contract. Exit 2 is
`hold`: valid evidence reports incomplete execution, missing/mismatched bindings,
unverified runtime capability/policy, failed/skipped fixtures, a non-completed
state or an absent execution log. Exit 1 indicates invalid, mismatched, changed
or incomplete input evidence. None authorizes dispatch, retry, resume, a freed
scientific-job slot, hold release or a schedule.

The journal opens through SQLite `mode=ro`. `LaunchJournal.evidence()` reads the
validated specification, acknowledgement and state in one snapshot. A return
cannot invent an acknowledgement for an uncertain submission. Inactive restored
journals can be inspected; they remain inactive. No result is written back into
an existing journal or historical run, and repeated reads are idempotent.

## Retained contract and bundle

The executable synthetic example is in
[`tests/test_cloud_return.py`](../tests/test_cloud_return.py). All identifiers and
observations there are fixtures, not a cloud qualification occurrence.

The return contract contains exactly `schema_version: 1`,
`kind: synthetic-return-contract`, `operation_key`, the journal's canonical
`spec_sha256`, a timezone-aware `frozen_at`, and 1–1,000 distinct `expected_tests`
IDs. Freeze it before outcomes. Its timestamp and prospective status are operator
attestations; a supplied date cannot prove an unexposed prospective design.

The return directory contains `manifest.json` and 3–64 explicitly listed files.
The manifest contains `schema_version: 1`,
`kind: synthetic-qualification-return`, `operation_key`, `spec_sha256`, `task_id`,
`contract_sha256`, the saved `acknowledgement_sha256`, `returned_at`, `files`,
`observation_path`, `test_report_path` and `log_path`. The three designated paths
must be distinct members of `files`; each entry records exact `bytes` and SHA-256.
Use portable paths under `artifacts/`, not reserved export filenames. Links,
junctions, traversal, unlisted/missing files, changed hashes and oversized inputs
are rejected. Limits are 1 MB per parsed JSON record, 32 MiB per retained file
and 256 MiB total. Empty logs are allowed for non-execution evidence.

The normalized runtime observation contains `schema_version: 1`,
`kind: synthetic-runtime-observation`, `operation_key`, `task_id`, `state`,
`execution_started`, `bindings`, `runtime_capability`, `policy_enforcement` and
`notes`. State is `completed`, `held`, `failed`, `cancelled`, `running` or
`unknown`; `execution_started` is an explicit boolean. Capability is `present`,
`absent` or `unknown`; enforcement is `enforced`, `not_enforced` or `unknown`.
Bindings name observed `source_revision`, `prompt_sha256`, `environment_sha256`,
`policy_sha256` and `account_scope_sha256`; unknown observations are null.
Every known binding is compared with the saved launch specification. A changed
terminal newline in delivered prompt bytes therefore remains a mismatch.

The fixture report contains `schema_version: 1`,
`kind: synthetic-fixture-report` and `cases`. Each case contains one expected
`test_id`, an outcome (`passed`, `failed`, `error`, `skipped`) and a reason.
Unknown/duplicate IDs and results contradicting reported non-execution are
rejected. Counts are recomputed from the cases. Missing, failed, errored or
skipped expected fixtures cannot count as a consistent completed return.

## Cloud-phase boundary

A completed agent turn with absent runtime capability and zero fixtures produces
a hold, even if the turn itself finished successfully. Policy-file similarity
does not establish current enforcement. No permission-failure cause is inferred.
These checks cannot verify that tests really executed or that an operator's
claimed runtime identity/enforcement observation is authentic.

This is a concrete L1/L2 result-reconciliation component. It does not supply the
missing live runtime capability, authoritative remote writer/fencing, provider
cancellation, PC-independent execution or durable scheduling. The
[existing native HOLD](qualification/NATIVE_RUNTIME_HOLD.md) and
[remote qualification sequence](REMOTE_AUTOMATION_ARCHITECTURE.md) remain in
force. There is no new observation from the held task, no replay of B4 and no
replacement occurrence. Choi remains closed, M6 disabled and Ravel unchanged.

Tests cover task/receipt/contract confusion, zero execution, prompt/policy/account
drift, incomplete and tampered transfers, missing/failed/skipped fixtures,
cancelled/unknown state, read-only journal access, inactive restores and CLI hold
exit status. Software consistency is separate from runtime qualification and
independent scientific-quality evaluation.
