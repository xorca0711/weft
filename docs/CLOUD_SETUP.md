# Cloud setup and first qualification handoff

This runbook prepares dot + Codex Cloud execution; it activates neither scientific
work nor schedules. [Roadmap](IMPLEMENTATION_PLAN.md) owns stages;
[environment specification](EXECUTION_ENVIRONMENT.md) owns qualification.

## Access and owner actions

**Completed, 11 October 2026:** private `weft-pilot` was published through the UI
at exact PR #1 revision `d031cef02ab4a417760bca46e90a63917d215d31`.
[Setup receipt](../records/cloud-setup-20261011.json): 58 tests, 15 pinned Ravel
files and a small synthetic export restored on a separate host. No new API secret
was needed. The steps below are the reusable runbook, not pending account actions.
Scientific runtime controls, fresh-task restoration and durable cloud outputs
remain separate qualification work.

1. In **Settings > Codex Cloud > Environments > Create environment**, prepare a
   private environment named **weft-pilot**, selecting Weft. Ravel remains a public,
   read-only pinned source; it need not be a full checkout or receive write access.
2. Use the setup brief below. Review its report and publish after the declared
   setup checks pass; return the environment name/ID and report or task link.
3. Choose the existing coordinating dot when its first handoff is ready. Initial
   delegation is a single explicit qualification task; recurrence belongs to M6.

The equivalent entry is **Work in > Cloud > Select environment > Create environment**.
These steps follow [OpenAI's environment guide](https://learn.chatgpt.com/docs/environments/cloud-environments).
Actual UI publication is confirmed in the receipt. Dot assignment and scientific
readiness are not implied. Keep setup results separate from later M3/M4 qualification.

## Exact source selection

The implementation is on [Weft PR #1](https://github.com/xorca0711/weft/pull/1),
branch `codex/discovery-review-buffer-20261011`; main may still be the earlier
scaffold. Resolve and record the full reviewed PR head SHA once during setup, then
pin qualification to it. Fetch the PR head into a fresh clean cloud checkout and
inspect its diff before selection. Never follow a moving branch during a job.
If merged first, record the merged revision containing this runbook. No merge is
requested by these instructions.

Ravel's source authority is `integration/ravel.lock.json`. Fetch its exact revision
without working-tree checkout or LFS downloads using the existing
[verification workflow](../.github/workflows/verify-ravel.yml). Read committed
blobs; historical Windows paths are provenance, not remote input locations.

## Network and credentials

| Stage | Initial destinations/access | Restriction |
|---|---|---|
| Setup/source verification | `github.com`; add observed transport/redirect hosts as needed | Weft checkout; public Ravel read; no broad token or Ravel publication credential |
| Manual discovery/reading smoke test | `www.ebi.ac.uk`, `europepmc.org` | Bounded existing adapters; access failures remain holds |
| Later M4 input preflight | `www.ncbi.nlm.nih.gov`, `ftp.ncbi.nlm.nih.gov` over HTTPS | Reviewed GSE145031 files and manifest hashes only; no FASTQ download |
| Later scientific dependencies | `pypi.org`, `files.pythonhosted.org` and exact required OS/package hosts | Versioned dependency plan and recorded setup traffic |
| Later artifact export | Qualified destination pending | Additional storage access only if existing product export fails qualification |

Use explicit domains and add blocked redirects based on observed need. This is a
proposed allowlist, not tested connectivity. The first standard-library preflight
needs no custom OpenAI API key, cloud billing account, SSH key or local-computer
connection. Configure any later credentials through product settings, not chat
or public repository files.

## Copyable environment setup brief

> Prepare a private Codex Cloud environment named weft-pilot for
> https://github.com/xorca0711/weft. Read AGENTS.md, AI_CONTEXT.md, PROGRESS.md and
> docs/CLOUD_SETUP.md from the reviewed PR #1 revision; record its full SHA.
> Keep scientific-execution and automation flags false. Use Python 3.12+ and Git;
> do not install or run historical scientific scripts. Run `python -m weft validate`
> and `python -m unittest discover -s tests -q`. Fetch only the Ravel revision in
> integration/ravel.lock.json without checkout/LFS downloads and run
> `python -m weft verify-ravel --repo <actual-cloud-ravel-git-path>`.
> Record actual architecture, versions and observable resource/network constraints.
> Check that a small synthetic artifact can be exported with a checksum and restored
> outside the original task; do not infer retention from its presence in one task.
> Report pass/hold/failure and exact remaining dependencies. Do not download datasets,
> run Choi analysis, change gate semantics, create schedules, merge, request broad
> credentials or provision paid external services. Preserve source pins and publish
> only after the setup report is reviewed.

Initial checks need no scientific packages. Numeric-stack installation, resource
enforcement and sparse-loader benchmarks are later stages. Setup can pass while
scientific readiness remains held.

## First dot handoff after M3 controls exist

Give the chosen dot a reviewed Weft revision, published environment identity and
one explicit scope. Request the synthetic qualification job in that environment,
its task ID and verified receipt, and holds for unknown outcomes instead of retries.
Verify actual cloud execution. This is initially a product task instruction, not
an automated API. Do not dispatch it before job/receipt validation code exists.

The dot's computer has separate files/sessions from the PC and can delegate into a
configured environment. [Official dot documentation](https://learn.chatgpt.com/docs/dots/computers-and-apps).
It must not infer claim acceptance, merge authority or a new RQ from job success.

## Readiness checkpoint

Capture environment ID/version, Weft SHA, Ravel pin verification, setup test result,
network/resources, synthetic export/restore, later M3 failure tests and dot
dispatch/return proof. Pending items remain holds in PROGRESS.md.

Work/Codex tasks consume product allowances; inactive API dollar-budget proposals
in policy.json do not meter subscription use.
[Official dot usage documentation](https://learn.chatgpt.com/docs/dots).
No API route or paid fallback is activated by architecture selection.
