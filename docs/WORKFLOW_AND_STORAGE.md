# Weft interfaces, backend and evidence storage

## Current architecture and historical storage

The [README workflow and backend diagrams](../README.md#intended-workflow) are
now the single diagram source. They distinguish implemented discovery/B3/manual
review from the proposed paper-to-analysis loop. Existing status and source-review
exports and a private fixture-backed scientific evidence view are available;
real scientific results remain pending.

The [evidence-generation roadmap](EVIDENCE_GENERATION_ROADMAP.md) owns W01–W12:
provisional workspaces, data/analysis contracts, bounded execution, numerical
critique, recovery, scientific decisions and optional Ravel handoff. The owner
delegated implementation of W01's provisional ownership separation. The
[offline workspace](EVIDENCE_WORKSPACE.md) now stores versioned source/case,
feasibility and contract records in a new explicitly configured private root.
Scientific execution remains held, and no historical storage is migrated.

Chat is the request/review interface. Existing Python commands, local catalogs,
source snapshots and saved returns provide the implemented backend. Google Drive
is recovery storage, not compute or a running shared database. GitHub Actions
checks software and provenance. Supported unattended dispatch, authoritative
remote coordination and recurrence remain unqualified.

The paper-flow and Choi storage details below describe the recorded 12 October
baseline. They are historical evidence, not instructions to reopen a closed pilot.
PROGRESS owns current status; EVIDENCE_WORKSPACE defines the separate private
provisional workspace paths and their implemented boundaries.

## Actual paper flow and gate coverage

The discovery adapter searches **Europe PMC**, including its indexed bibliographic
records, through three configured streams: broad, contrary and adjacent. It does
not currently run a direct Cell/Nature/Science publisher crawler. PMC open-access
XML and publisher/supplement/dataset sources are reviewed later when accessible
and permitted. Journal preference is not a scientific gate or proof of peer review.

The latest qualified cloud batch used A0/A1 context and a frozen index-date window
of 12 September–12 October 2026. Its **82 observations deduplicated to 74 papers**,
with **148 proposed paper/RQ links**. These are the same exposed profile/window
used in development, not a second independent set of 74 papers.

| Stage | Fresh-candidate track | Separate Choi benchmark |
|---|---|---|
| G0/G1 resource, identity and access checks | Bounded retrieval/deduplication worked; comprehensive correction/version coverage remains incomplete | Frozen source/input/runtime and recovery checks qualified for this attempt |
| G2 reading relevance | 5 links across 3 papers: 1 read next, 1 hold, 3 link rejections; 143 deferred | Previously read, deliberately exposed benchmark |
| Selected-text assessment | 1 OA XML inspected; four source-bound statements remain held | Paper/figure/supplement comparison completed |
| G3 dataset eligibility | No fresh candidate has completed figure/supplement/dataset-use review; B3 proposal records remain held | Description allowed; animal-level treatment-effect inference unsupported |
| G4 execution readiness | No fresh-candidate scientific job authorized | Qualified frozen contract, source, runtime, resource and output isolation |
| G5 reproduction/QC | Not reached | One adapted descriptive run, QC and discrepancy review complete; exact five-state reproduction unsupported |
| G6/G7 extension and question contribution | No accepted extension or new RQ | No additional analysis; owner retained a descriptive discrepancy benchmark, no new RQ or causal claim |
| G8 integration | No fresh-candidate result admitted into Ravel | Public outputs, unchanged receipt, clean-checkout CI and owner retention; Ravel #149 merged |

G0–G8 is the [gate specification](GATES.md), not a fully implemented autonomous
state machine. Mechanical checks, proposal consistency and manual scientific
review are different kinds of evidence. “Read next” does not mean data eligible,
scientifically accepted or ready to run. The cloud/local screening runs also
disagreed on one link; independent screening accuracy is not established.

The detailed evidence is in [cloud screening](SCREENING_CLOUD_QUALIFICATION.md),
[the full candidate list](../records/backend-candidates-20261012.csv),
[B3/B4 interruption](B3_CLOUD_B4_REVIEW.md), and
[Choi publication/retention](M5_PUBLICATION_PLAN.md). B4 is held after platform
filtering interrupted material acquisition; final interrupted state is unverified.

## Where evidence is stored

Passing an early gate does **not** copy material into Ravel. Weft keeps its
private run records, cached source snapshots, packets and proposals in the
selected `runs/<store>/` directory, with `catalog.sqlite` as its database.
Public summaries and receipts go under `records/`. Private checkpoints use the
owner-only Drive folder; they are not public Ravel evidence.

The owner requested a separate Ravel intake for reviewed trial packages. Choi's
three scientific dossier documents have moved to `weft_intake/choi-2020-p001/v1/`,
with five exact public receipt snapshots and a transfer manifest. Weft retains
navigation stubs and its operational/history records. Existing Ravel frozen
outputs remain in their contract-bound locations. The intake is a trial handoff
collection, not an automatic importer or a new canonical RQ registry.

The migration is integrated in [Ravel #150](https://github.com/xorca0711/ravel/pull/150).
Start at [Ravel intake](https://github.com/xorca0711/ravel/tree/main/weft_intake).

For Choi, paths **relative to a Ravel checkout** are:

| Material | Location |
|---|---|
| Migrated Weft trial dossier: pilot plan, source/input review, scientific summary and five receipt snapshots | `weft_intake/choi-2020-p001/v1/` |
| Paper-specific methods, scientific review, publication guide and human disposition | `Research Article/gate1_02_choi_2020/weft_pilot_v1/` |
| Original receipt, figures, tables and restored matrix | `analysis/research/runs/p001_figure1_v1_f001_d56ee41e13cd4327/` |
| Immutable archive identity/member hashes for restoration | `analysis/research/published_outputs/choi_figure1_v1.json` |
| Registered contracts and receipts | `analysis/research/registry.json` |
| Reviewed input provenance / locally retained source data, when present | `raw_data/GSE145031/weft_pilot_v1/` (ignored; not populated by output restoration) |

The receipt, lock and documentation are tracked in Git. The 15 output files,
including the 385,675,968-byte H5AD, are distributed in the
[public release](https://github.com/xorca0711/ravel/releases/tag/choi-p001-figure1-v1)
and restored into the run directory with:

```bash
python analysis/scripts/restore_published_outputs.py
```

Output files remain ignored rather than being added to ordinary Git history.
The command checks hashes and refuses conflicting local files; it does not rerun
analysis or fetch raw inputs. Actual absolute paths depend on which Ravel checkout
is being used. A merged GitHub main does not update an older local worktree.

Future admitted papers need their own reviewed article directory, contract and
versioned run identifier. They must not reuse the Choi path or automatically
become canonical `RQ_Specified/A*` questions. No new canonical RQ was created here.

## Further development

Follow [W01–W12](EVIDENCE_GENERATION_ROADMAP.md#implementation-jobs-and-completion-evidence)
for the proposed evidence-generation work and cloud dependencies. Preserve the
frozen B5 evaluation and retain outcome exposure in any prospective amendment.
B4 remains held/excluded, Choi closed and M6 disabled. A fresh scientific case
requires reviewed ownership, a bounded contract and a qualified permitted runtime;
no new worker, dispatch or Ravel write follows from this guide.
