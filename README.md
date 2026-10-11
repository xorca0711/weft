# Weft

**Agent workflows for literature discovery, reproducible reanalysis and research-question development.**

| Capability | Status | Evidence | Boundary |
|---|---|---|---|
| Local scaffold and pinned Ravel connection checks | Descriptive only | [Validation record](records/bootstrap-validation.json) | Software checks; no scientific validation |
| Manual literature discovery and RQ review buffer | Descriptive only | [Live validation](records/discovery-validation.json) | Metadata matches and reading priority, not accepted claims |
| Manual source-bound reading packets | Descriptive only | [Local reader](docs/LOCAL_READER.md) | XML text/captions; semantic and figure review remain separate |
| Choi figure, supplement and input review | Descriptive only | [Review receipt](records/pilot-review-20261011.json) | Manual review and file integrity; numerical analysis remains held |
| Pinned Codex Cloud setup | Descriptive only | [Setup receipt](records/cloud-setup-20261011.json) | Private environment published; small export verified; science remains held |
| Dot coordination and scientific cloud execution | Not established | [Cloud roadmap](docs/IMPLEMENTATION_PLAN.md) | Runtime controls, durable artifacts and delegation remain unqualified |
| Autonomous paper-to-question workflow | Not established | [Implementation plan](docs/IMPLEMENTATION_PLAN.md) | Scientific workers, unattended agents and Ravel export remain planned |

Weft is being built to bring new literature into an existing research programme:
find papers against established questions and broader reading interests, explain
their relevance, qualify reusable data, and coordinate bounded reproduction and
exploratory analysis. The intended output is a traceable evidence package,
including negative results, discrepancies and candidate questions.

The name comes from the crosswise threads of woven fabric. **Weft** is the
project name; `weft` is the repository and Python module name. It is not an acronym.

[Ravel](https://github.com/xorca0711/ravel) owns the biological questions,
scientific methods and evidence. Weft owns the automation that connects papers
and jobs to that research. Personal career interests remain in an untracked
private configuration, even though this repository is public.

## Intended workflow

The selected deployment uses a dot for coordination and Codex Cloud for execution.
The initial cloud environment is published; numerical work remains unqualified. Solid arrows show
implemented manual stages. Dotted arrows show the remaining
scientific workflow. An RQ supplies search context; the review buffer keeps proposed
relationships separate from accepted evidence.

```mermaid
flowchart TD
    R["Pinned Ravel RQ context"] --> D["Discover metadata and resolve paper identities"]
    Q["Broad, contrary and adjacent queries"] --> D
    D --> B["Review buffer: proposed paper-to-RQ links"]
    B --> T["Reading priority: read next, hold or reject"]
    T --> P["Source-bound reading packet: manual baseline"]
    O["Dot coordinator: planned"] -.-> P
    P -.-> V["Review findings, units, limitations and RQ compatibility"]
    V -.->|eligible data| C["Freeze contract and qualify Codex Cloud runtime"]
    O -.-> C
    V -.->|unknown or unsupported| H["Hold or reject link; retain evidence"]
    C -.-> A["Reproduce a defined result; retain discrepancies"]
    A -.-> E["Bounded extension and interpretation"]
    E -.-> N["Article-local question or evidence update"]
    N -.-> X["Reviewable Ravel PR"]
    X -.->|authorized integration| R
```

## Read what you need

| If you want to… | Read |
|---|---|
| Run bounded searches and inspect receipts | [Discovery guide](docs/DISCOVERY.md) |
| Understand why a paper is not immediately supporting evidence | [Decision buffer](docs/DECISION_BUFFER.md) |
| See the full development roadmap and current stage | [Implementation plan](docs/IMPLEMENTATION_PLAN.md) |
| Understand agent responsibilities and context | [Agent workflow](docs/AGENT_WORKFLOW.md) |
| Inspect automated decisions and stopping rules | [Gate specification](docs/GATES.md) |
| Connect Weft to Ravel without competing sources of truth | [Integration contract](docs/RAVEL_CONNECTION.md) |
| Run the first complete paper pilot after implementation | [Choi 2020 pilot](docs/PILOT_CHOI_2020.md) |
| Inspect completed figures, supplements and dataset qualification | [Choi review](docs/PILOT_CHOI_REVIEW.md) |
| Configure the selected cloud environment and access | [Cloud setup runbook](docs/CLOUD_SETUP.md) |
| Qualify the scientific runtime | [Execution environment](docs/EXECUTION_ENVIRONMENT.md) |
| Evaluate missed papers, extraction and analysis fidelity | [Evaluation plan](docs/EVALUATION.md) |
| Check completed work and remaining dependencies | [Current state](PROGRESS.md) |
| See authorship, decisions and revisions | [Development record](DEVELOPMENT.md) |

## Try it yourself

Python 3.12+ and Git are sufficient. No API key, datasets or scientific packages
are needed for validation or manual metadata searches:

```bash
git clone https://github.com/xorca0711/weft.git
cd weft
python -m weft validate
python -m unittest discover -s tests -q
```

To verify the Ravel pin and referenced Git objects, use an existing clone that
contains the revision in [ravel.lock.json](integration/ravel.lock.json):

```bash
python -m weft verify-ravel --repo /path/to/ravel
```

Use the [discovery commands](docs/DISCOVERY.md) to search and inspect the buffer,
then the [manual reader](docs/LOCAL_READER.md) to prepare an eligible paper.

The verifier reads **committed blobs at the pinned revision**, so local edits are
neither consumed nor overwritten. It does not run historical analysis scripts,
download datasets, connect an AI account, or write to Ravel.

## Execution and scientific boundaries

The owner selected a dot to coordinate and Codex Cloud to execute versioned code,
starting with manually dispatched qualification. No additional local PC is required.
The [roadmap](docs/IMPLEMENTATION_PLAN.md) puts job limits, state recovery and artifact
export before the numerical pilot. GitHub CI remains for deterministic tests.
Cloud selection does not establish available RAM, runtime limits or scientific readiness.

The first paper is a deliberately exposed historical benchmark, **Choi et al.,
Cell Stem Cell (2020)**. Completing it would test workflow fidelity and correct
holds, not establish new biology or performance on unseen papers. Fresh-paper
evaluation follows separately. A candidate question is not scientific acceptance.

No scheduled searches, paid API calls, scientific runs, automatic merges or
GitHub-to-local execution are enabled by cloning this repository.
