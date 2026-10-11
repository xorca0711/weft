# Sources and preparation record

Inspected 11 October 2026. These references inform the plan; they do not establish
account access, a provisioned worker, deployed automation or completed reproduction.

| Source | Use and access scope |
|---|---|
| [Ravel at the pinned main revision](https://github.com/xorca0711/ravel/tree/bfe26b876221cf6c6fa6f9b16a90cfb516b5998d) | Registry, governance, current paper records and pilot limitations inspected from committed/local repository sources; per-file hashes in integration lock |
| [Choi 2020 primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7487779/) | Published XML, institutional main figures, all S1-S7 figures/legends and fresh GEO metadata inspected; editions, transport limits and exact coverage in [pilot review](PILOT_CHOI_REVIEW.md) |
| [Europe PMC REST service](https://europepmc.org/RestfulWebService) | Official indexed API documentation inspected; direct documentation fetch returned 403. Live metadata and XML adapters tested; receipts in records/discovery-validation.json |
| [EMBL-EBI programme access guidance](https://www.ebi.ac.uk/training/online/courses/embl-ebi-programmatically/europe-pmc-programmatically/) | Official source for publication metadata, references and data-link access |
| [OpenAI dots](https://learn.chatgpt.com/docs/dots) | Official page inspected: cloud agent, connected services, local computer availability; user-specific access not checked |
| [Codex GitHub Action](https://learn.chatgpt.com/docs/github-action) | Official page inspected: noninteractive agent execution inside GitHub workflows; no agent job activated here |
| [GitHub Actions limits](https://docs.github.com/en/actions/reference/limits) | Hosted jobs have a six-hour limit at inspection; compute placement must account for runtime/storage |
| [GitHub workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) | Schedules may be delayed/dropped; public inactive schedules may be disabled. Durable catch-up is a design requirement |
| [ASReview research](https://www.nature.com/articles/s42256-020-00287-7) | Precedent for assisted literature screening; not a validation of Weft or automated scientific merit |
| [Improving Active Learning in Systematic Reviews](https://arxiv.org/abs/1801.09496) | Primary methodological precedent concerning selection toward similar records |

Searches used during concept/preparation: OpenAI dots and Codex GitHub Action;
GitHub Actions limits/schedule behavior; Europe PMC REST search/publication dates;
Choi paper title with Figure 1 and GSE145031. This was a bounded architecture and
pilot-source check, not a systematic literature review or novelty clearance.

No full article, annotated PDF or private owner context is republished in Weft.
