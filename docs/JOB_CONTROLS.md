# Job-control foundation

This is the first M3 implementation slice on a follow-up branch. The cloud setup
baseline remains PR #1 revision `d031cef02ab4a417760bca46e90a63917d215d31`.
Nothing in this module launches a process, calls a cloud API or permits science.

## Implemented and tested

`weft/jobs.py` provides a coordinator-owned SQLite ledger for **synthetic
qualification only**. A normalized packet binds paper/context/policy/contract/
executor identities and an input manifest. Submit is idempotent; changed identities
or parameters create a different job. Input files are verified before claim.

A transaction reserves one execution slot across cooperating clients of the same
database. Attempts remain visible with append-only transition events. Lease expiry
records an unknown outcome and keeps the slot reserved; it never assumes the
worker stopped. Cancellation requests likewise retain the slot. Retry count is
bounded; stale context/policy and a backwards clock prevent dispatch. Direct event
update/delete and packet update are rejected by SQLite triggers.

The terminal-report API currently records self-reported synthetic failure or
cancellation with a content-addressed receipt reference. It does not independently
verify process termination, receipt contents or actor identity. It cannot record
success. It is not suitable for scientific dispatch or adversarial clients.

```bash
python -m unittest discover -s tests -p test_jobs.py -q
```

Tests exercise competing connections, duplicate submissions, input mutation,
stale context/policy, lease expiry across restart, cancellation, token mismatch,
retry exhaustion and immutable history. They are software fixtures, not an actual
cloud worker or proof of durable remote storage.

## Required next slices

1. A trusted executor adapter and content-verified terminal receipts bound to job,
   attempt, input/code hashes and actual process status; unknown outcomes stay held.
2. Verified output manifests, externally exported artifacts and restore testing.
3. Actual runtime memory/time/process-tree limits and cancellation qualification.
4. Authoritative ledger hosting/recovery and supported product task dispatch.
5. Product-route usage budgeting and reviewed scientific-gate integration.

The SQLite file must have one authority. Copying it into separate Codex Cloud tasks
creates separate ledgers, not a distributed lock. Triggers are integrity checks
for cooperating clients, not protection against an administrator editing the file.
The synthetic module has no scientific success/acceptance path. Existing policy
flags and scientific validators remain unchanged.
