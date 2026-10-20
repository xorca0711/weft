# Manual workflow coordinator

The coordinator composes the existing bounded discovery, screening handoff,
XML reading and B3 proposal components. It provides one next action at a time,
saved-return recovery, and a private JSON/HTML status export. It invokes no model
and has no app, browser, CLI cloud, scheduler or alternate-provider launch path.

The [selection and material-review extension](SELECTION_AND_MATERIAL_REVIEW.md)
adds versioned paper-first nomination, verified XML reuse, local manifest intake
and a source-linked review bundle. Existing frozen batches retain their policy.

This implementation is local software qualification. It does not qualify an
unattended deployment, fresh-paper review quality, scientific acceptance or a
new biological run. Ravel is read only when building the pinned search context.

## Start and operate

Use a **new private store** for an explicitly authorized new batch. Creating a
workflow freezes the existing search specification and caps without searching.
The dates below describe a retrieval window, not a work schedule. Substitute the
intended repository, profile, dates and a stable actor label. Actor labels are
attribution, not authentication.

```powershell
python -m weft workflow-create --repo X:/GitHub/ravel --profile alveolar-transitions --since 2026-10-01 --until 2026-10-02 --store runs/new-review --actor reviewer
python -m weft workflow-status --store runs/new-review --batch BATCH_ID
python -m weft workflow-advance --store runs/new-review --batch BATCH_ID
```

`advance` returns the next packet, current outcome or `needs_network`. Add
`--allow-network` only for an intended bounded metadata or XML retrieval. An
interrupted or failed retrieval is never automatically reconciled or replayed.
Each command is bounded; there is no daemon or background loop.

| Returned stage | Operator action | Existing component used |
|---|---|---|
| Discovery pending | Explicit `advance --allow-network` | `batches.run` and its frozen budgets |
| `screening` | Review `issued.packet`; fill its exact response template | `handoff.claim` / `screening.submit` |
| `material` | Verified same-batch XML reuse or explicit retrieval; inspect any access/integrity hold | `screening.read_packet` |
| `reading` | Read the returned material directory's `packet.json` and `prompt.txt`; prepare its reading assessment | `screening.submit_reading` |
| `evidence` | Review resource coverage and separate data/RQ proposals; fill the exact template | `qualification.issue` / `qualification.submit` |

Submit the review using its stage and the actor bound at creation:

```powershell
python -m weft workflow-submit --store runs/new-review --batch BATCH_ID --stage screening --assessment private/screening.json
python -m weft workflow-submit --store runs/new-review --batch BATCH_ID --stage reading --assessment private/reading.json
python -m weft workflow-submit --store runs/new-review --batch BATCH_ID --stage evidence --assessment private/evidence.json
```

Use the existing `batch-attach-evidence` command for explicitly supplied figure
or supplement files, or use `workflow-import-materials` with a hash-bound local
manifest. The coordinator does not download source-proposed URLs,
render attachments, attest inspection or execute author code. The existing
source, citation, coverage, unit, lineage and proposal validators are unchanged.

Only fresh unstarted batches may opt in. `workflow-init --store STORE --batch
BATCH_ID --actor reviewer` recovers creation interrupted after the batch was
saved but before workflow initialization. It refuses a batch with prior searches,
candidates, review handoffs or a second batch in its catalog. Existing pilot
catalogs are **status/export only** through this interface. This is not an
authorization to create a replacement for a held pilot.

## Recovery and holds

- A response is saved before component ingestion. If acknowledgement is lost,
  `workflow-status` shows its return ID. Use `workflow-recover --store STORE
  --batch BATCH_ID --return-id RETURN_ID` to ingest those same saved bytes. Exact
  resubmission is also idempotent. Recovery performs no source retrieval or model
  dispatch and reuses the original validators.
- Invalid saved responses remain pending and block new submissions. Recovery
  does not turn invalid data into valid data; there is no force-replace command.
  Preserve the return for explicit operator review.
- Lost packet output can be read with `advance` again. The same screening claim
  and evidence packet are returned. This is not permission to dispatch a second
  worker. Expired or ambiguous claims are never reassigned.
- Searches left `running` and material requests left
  `reading-started-outcome-unknown` remain held. A reading assessment requesting
  `hold` never advances into B3 through this coordinator.
- `workflow-hold --store STORE --batch BATCH_ID --reason "Reason"` persists an
  operator hold. There is deliberately no implicit release, replacement or
  resume-through-hold option.
- A copied/restored catalog is inactive for mutations because its host/path
  binding no longer matches. It can still be viewed and exported. This preserves
  the existing handoff restore guard; it is not distributed fencing.
- An interrupted export has no completion manifest. Retain it as incomplete and
  export into a new directory; no export overwrites an earlier snapshot.

Use one operator and one dedicated batch catalog. Coordinator calls have a local
OS lock; components keep their existing locks and transactions. Do not run legacy
mutating commands concurrently with the coordinator. Low-level component APIs
remain available and are not a universal authorization boundary. Existing explicit
component reconciliation/amendment procedures require their own review; this
coordinator does not select or execute them automatically.

## Status and export

```powershell
python -m weft workflow-export --store runs/new-review --batch BATCH_ID --output private/review-snapshot-001
```

The new directory contains `status.json`, `index.html` and a last-written
`manifest.json` with the SHA-256 hashes of both outputs. Open `index.html` locally.
It contains no scripts, remote assets or active source links; source text is HTML
escaped. The snapshot is private: titles, reasoning, exposure statements, source
identities and local binding information can be sensitive. It copies no source
XML, full-text directory or attachment and never uploads anything.

For source text, citation navigation and optional supplied attachment copies,
use the separate private `workflow-review-export` described in the extension.

Status/export use a read-only SQLite connection and a consistent database read
transaction. They neither initialize schemas nor resume a run. Source files must
remain quiescent while exporting; a database snapshot does not lock external files.

The view distinguishes discovery completion, screening decisions, material
preparation, reading review, resource-coverage holds, data-use proposals and RQ
compatibility proposals. Proposal details retain comparison, measured endpoint,
biological unit, source/data lineage, citations, limitations and actor exposure.
Paper counts and link counts are not independent-study counts.

`complete` means no coordinator action remains in the bounded batch.
`complete_with_holds` retains held or cap-deferred links and held proposals.
Neither means scientific success. `all_evidence_reviews_recorded` is false for
empty batches, rejected/deferred links and incomplete reviews. CLI exit code 2
signals `hold` or `complete_with_holds`; malformed input errors return 1. A
successful private export returns 0 even when its snapshot contains holds.

## Platform integration constraint

The view carries the dated 13 October evidence, not a live health probe:

| Surface | Established observation | Remaining uncertainty |
|---|---|---|
| CLI | No named environment; known app worker ID rejected | Routing/version compatibility and effective account/workspace mapping |
| Native app child | Creation admitted; runtime-status capability absent; zero tests | Why the required capability was not exposed |
| Browser | Loaded origin `allow` setting disagreed with observed denial | Which active policy produced the denial |

The owner confirms granting the requested access. The implementation does not
ask for the same grants again. Permission grant, environment resolution, task
admission and runtime capability exposure are separate observations. The leading
engineering inference is a platform integration mismatch; its root cause is
not established by the stored evidence.

Official documentation inspected on 20 October distinguishes current and legacy
[cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)
and documents an environment identifier for
[CLI cloud commands](https://learn.chatgpt.com/docs/cli/reference). This makes route
compatibility a plausible investigation target, but does not prove the installed
CLI used an incompatible route. No product repair is claimed.

Automatic launch remains absent until supported environment mapping and runtime
capability evidence are established and the existing qualification gates pass.
Retry loops, another provider or more privileges would not establish those facts.
Choi stays closed, B4 held, M6 disabled, and exact delivered-prompt binding remains
unqualified. See the original [access diagnosis](LAUNCHER_ACCESS_DIAGNOSIS.md),
[native HOLD](qualification/NATIVE_RUNTIME_HOLD.md) and
[B4 record](B3_CLOUD_B4_REVIEW.md). The prepared support request remains unsent.

## Verification

`tests/test_workflow.py` uses synthetic source fixtures and injected failures,
without network/model calls. It covers stage progression, saved returns and lost
acknowledgements across screening/reading/B3, process reopen, discovery and
material interruption, caps, stale/tampered evidence, explicit/expired holds,
inactive restored catalogs, read-only status, escaped immutable exports, and CLI
creation. Run the targeted suite and repository checks:

```powershell
python -m unittest discover -s tests -p test_workflow.py -q
python -m weft validate
python -m unittest discover -s tests -q
```

These tests establish bounded software behavior, not semantic review accuracy or
live platform integration. New workflows use the versioned nomination extension;
historical ordering and scientific evaluation policy remain unchanged. Further
launch work requires new platform evidence; independent
review-quality evaluation remains separate.
