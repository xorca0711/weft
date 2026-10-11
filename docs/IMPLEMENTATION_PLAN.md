# Implementation plan

## Objective and completion criterion

Build an agent-operated system that discovers papers, explains relevance to
existing research, qualifies reusable data, reproduces bounded published results,
investigates justified extensions and prepares traceable evidence for Ravel.
Routine transitions should run under a standing scope/resource policy. Missing
evidence produces a hold; scientific acceptance remains distinct from execution.

The first end-to-end release is complete when the [pilot](PILOT_CHOI_2020.md)
travels from a recorded discovery query to a reviewable Ravel evidence package,
including its required inferential hold and candidate/no-candidate disposition.
A scientifically positive result or a new canonical RQ is not required.

## Architecture

| Layer | Implementation target | Durable output |
|---|---|---|
| Source adapters | Europe PMC first; publisher feeds and citation traversal next | Query, response hash, cursor, UTC window, provider and version records |
| Context builder | Read pinned Ravel registry, current result/amendment, guide and contract | Small source-addressed RQ context packet |
| Agent adapter | Backend-neutral tool calls; initial Codex CLI/SDK or supported dot integration | Structured assessments, model/tool versions and evidence locators |
| Gate/state service | Typed decisions, explicit transition graph, SQLite initially | Append-only events, artifacts, holds, attempts and resource ledger |
| Scientific worker | Dedicated Linux environment with read-only inputs and separate outputs | Frozen contract, environment lock, QC, measured results and receipt |
| Ravel exporter | Validate base revision and produce a scoped branch/PR | Evidence package, current-summary edits and integration report |
| Private preferences | Local ignored file or separately permissioned store | Career reading profile; never exported to public artifacts |

One coordinator may perform several roles sequentially. Multiple agents are an
implementation option, not a requirement or proof of independent review.

## Milestones and acceptance

| Milestone | Tasks and artifacts | Done when | Dependency/status |
|---|---|---|---|
| M0: foundation | README diagram, ownership, gate specification, pilot draft, Ravel lock, offline checks | Local checks and public CI pass; limitations are explicit | Implemented scaffold; see PROGRESS |
| M1: discovery | Europe PMC adapter; broad/contrary/journal queries; conservative deduplication; provider version/correction links; receipts and cutoffs | Bounded source retrieval and failure tests pass; complete version families and recall are evaluated separately | Manual baseline implemented; see discovery validation record |
| M2: reading agent | Source extraction, bounded RQ packets, reading/career queues, relevance explanation and abstention | Every recommendation points to inspected evidence; access limits retained; evaluated against independently reviewed records | Partial: pinned context, manual local Codex packet and locator checks implemented; evaluation outstanding |
| M3: gate engine | Explicit state transitions; structured decision schema; idempotent jobs; budgets; lock/lease; failure recovery | No transition without required evidence; tampered receipts, missing units, unknown outcomes and duplicate jobs rejected | Requires M1; can develop alongside M2 |
| M4: scientific worker | Inspect pilot inputs; write a versioned Ravel contract/adapter; freeze environment; run QC and bounded reproduction | Required data joins and hashes verified; old outputs untouched; discrepancy ledger and negative controls preserved | Requires M2/M3 and qualified worker |
| M5: synthesis and export | Precedent review; candidate/no-candidate report; artifact manifest; safe PR export; CI | One reviewable Ravel package with current base checks, evidence links and explicit acceptance status | Requires M4 |
| M6: prospective qualification | Freeze discovery/evaluation criteria, then assess newly arriving papers; controlled recurring operation | Reviewed acceptance criteria met across inclusion, extraction, compute and interpretation; measured costs and holds reported | Requires M5; no automatic rollout from M0 |

Each milestone should be one or a small number of scoped PRs, with its tests and
observed limitations. The M1 smoke test precedes the paper reading stage.

The owner selected local Codex with manual runs for M2. Discovery links enter the
[decision buffer](DECISION_BUFFER.md); no direct claim join is allowed. The initial
full-text keyword query overmatched, so recent profiles now use title/abstract
fields and preserve the earlier receipts. Oversized windows require explicit
partitioning. Full version reconciliation, correction-feed refresh, source-support
evaluation and job-resource enforcement remain qualification work, not completed
features inferred from the smoke test.

## Proposed software layout

Current files: `weft/` discovery, context, buffer, manual reading and validation CLI; `configs/`; `integration/ravel.lock.json`;
`tests/`; `docs/`; small public `records/`.

Future modules: `weft/sources/`, `weft/context/`, `weft/agents/`,
`weft/gates/`, `weft/jobs/`, `weft/executors/`, `weft/integrations/ravel/`.
Add modules as implemented; empty placeholders are not functionality.

Core records: PaperVersion, SourceEvidence, RQContext, ScreeningDecision,
DatasetQualification, AnalysisJob, GateDecision, RunReceipt, CandidateQuestion,
IntegrationPackage. All carry schema versions and stable IDs; records distinguish
observed facts, model proposals and authorized decisions.

## Operating policy

Start with manual dispatch. After qualification, propose weekly discovery plus
resumable job processing. Store the last successful query window; use overlapping
date windows and identity deduplication to catch late indexing. Backfill missed
windows after outages. A GitHub schedule is a trigger, not the durable state store.

Use a unique job key from paper version, RQ-context hash, policy version, contract
hash and executor version. A lease prevents concurrent duplication. Retries append
attempt records; a new scientific parameter choice creates an amended job rather
than concealing the failed attempt. Write checkpoints before long external work.

Proposed initial bounds are in `configs/policy.json`: one active scientific job,
bounded literature retrieval and model use, wall time and download/storage caps.
These are engineering limits, not sample-size or significance thresholds. Provision
hard usage limits as well as estimates; unknown model pricing or unmetered calls
must hold paid execution. No budget is presently activated.

## Deployment

- GitHub CI: deterministic checks on ordinary hosted runners; no private data.
- Discovery: a scheduled job or cloud agent with a durable receipt store.
- Analysis: dedicated worker/VM with persistent data, an isolated environment and
  short-lived access to required artifacts. Do not attach a public-PR-triggered
  runner directly to a personal research desktop.
- Dots can coordinate through connected tools when available. Backend adapters
  must preserve contracts, state and artifacts outside chat history.
- Allow author-code execution only within the qualified worker, with pinned
  dependencies, constrained network access and no publication credentials.
- Store large files outside Git; export compact manifests and appropriate figures.

GitHub-hosted job limits and scheduled-trigger behavior are recorded in
[sources](SOURCES.md). No paid service, compute resource or recurring task is
configured by this plan.
