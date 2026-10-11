# Current project state

**Update this before stopping work, every session.**

## Initial public repository — 11 October 2026

The owner requested a separate implementation-plan repository, a concrete Ravel
connection, agent workflow, automated gates, a first paper pilot, and a workflow
diagram in the main README. Public visibility was explicitly selected.

Completed: architecture and staged implementation plan; agent/gate specifications;
revision-pinned Ravel connection; historical Choi 2020 pilot contract draft;
offline validator and read-only connection verifier; tests and CI configuration.
Local validation passed: 11 unit tests, 20 documentation links and all 15 pinned
Ravel source files. The [record](records/bootstrap-validation.json) contains code/
configuration hashes and the exact scope. The initial sandbox invocation could
not use temporary Git fixtures; the unchanged tests passed outside that restriction.
Published at https://github.com/xorca0711/weft, with the physical local checkout
at `X:\GitHub\weft`. Initial GitHub checks passed, and the independently fetched
Ravel revision passed all 15 source-identity checks. The [remote validation record](records/remote-validation.json)
links both completed runs at bootstrap commit `022aa6d`. The README Mermaid
diagram was inspected in GitHub's rendered view. Later commits receive normal CI;
the Actions page owns their current status.

Not implemented: live discovery, model calls, durable task scheduler, scientific
execution adapter, candidate generation and Ravel PR exporter. No biological
pilot has run. No API credentials, runner registration or recurring automation
has been configured. The Ravel directory migration remains deferred.

Next work, in order:
1. Implement M1 source discovery, version reconciliation and query receipts.
2. Implement M2 bounded context extraction and evidence-backed screening; evaluate
   missed papers and source support before using rankings to route work.
3. Implement M3 machine-enforced gates, durable job state and resource accounting.
4. Qualify M4's isolated worker and new Ravel contract without rerunning historical
   scripts in their frozen directories. Establish the pilot's input hashes and
   runtime lock, then execute its bounded descriptive reproduction.
5. Complete M5 integration as a reviewable evidence PR; qualify M6 on unseen papers.

External decisions: agent-account/backend availability, worker location and budget,
full-text access, source-data availability and scientific contract acceptance.
The operational caps in configuration are proposals, not spending authorization.
