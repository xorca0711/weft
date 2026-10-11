# Current project state

**Update this before stopping work, every session.**

## Choi source review and worker recommendation — 11 October 2026

Work continues on `codex/discovery-review-buffer-20261011` in
[PR #1](https://github.com/xorca0711/weft/pull/1), against Weft main
`59aa0f740b8e3d6d856684ef7052f5e7d77b7820`. The read-only Ravel pin is
`bfe26b876221cf6c6fa6f9b16a90cfb516b5998d`. No Ravel data, worktree or result was changed.

The [roadmap](docs/IMPLEMENTATION_PLAN.md) separates implemented discovery/manual
reading from the remaining screening evaluation, runtime controls, scientific
execution and export. Local Codex manual reading remains the owner's selection.

Completed this session:

- Reviewed all main figures and S1-S7, with detailed Figure 1B-D/S1 inspection.
  Verified the recovered official supplement's pages against the institutional
  edition after accounting for its publisher cover. Preserved access failures.
- Mapped all 12 GEO samples across the three linked accessions. Qualified the
  three Tomato-positive input identities, archive/member hashes, lengths, selected
  gzip CRC/entry totals and identifier joins within the recorded audit scope.
- Recorded raw barcode versus cell distinction, pooling, the unresolved 173-cell
  arithmetic remainder, published/adapted QC and annotation differences, and the
  four-ATAC-sample/two-processed-track limitation.
- Recommended a separate Linux x86-64 worker, preferably 32 GiB RAM; documented a
  conditional 6 GiB Windows fallback. No host was selected or provisioned.
- Synchronized pilot configuration, README, source index and handoff. Ravel's
  migration is complete: physical `X:/GitHub/ravel`, compatibility junction removed,
  data and seven worktrees preserved by the separate migration verification.

[Source review](docs/PILOT_CHOI_REVIEW.md), [review receipt](records/pilot-review-20261011.json),
[input manifest](records/pilot-inputs-20261011.json) and
[environment recommendation](docs/EXECUTION_ENVIRONMENT.md) own the details.
Full texts, images and audit scripts remain ignored under `runs/pilot-review-20261011-v1`.
The initial [reading assessment](records/pilot-reading-20261011.json) is preserved.

No numerical analysis, independent screening evaluation, new RQ, scientific
acceptance, worker launcher, paid service or recurring automation ran. The pilot
remains `planned-not-run`; structural integrity does not activate its gates.

## Exact next steps and decisions

1. Select an available scientific host. Preferred: separate Linux x86-64, 4 vCPU,
   32 GiB RAM, proposed 16 GiB job cap. Conditional local fallback requires a new
   environment on X:, 6 GiB cap and at least 10 GiB available RAM. Budget and any
   external provisioning require a concrete decision; neither is configured.
2. Implement M3 job identity/lease, immutable references, attempt history,
   cancellation and enforced resource limits. Test failure cases with synthetic
   fixtures. Source and buffer policy changes still require explicit review.
3. Prepare and review a new Ravel contract/adapter and environment lock. Preserve
   published versus adapted QC, prior exposure and all historical outputs. Qualify
   coordinate/value validity, sparse-loader memory and comparison criteria.
4. Run P001 only after those conditions pass, then prepare the reviewed Ravel
   export. An absent pAT2 call or no new RQ is a legitimate recorded outcome.
5. Continue M2 source-support evaluation and M1 correction/version-family work;
   qualify an unseen-paper pilot before proposing recurring automation.

Earlier discovery evidence: **58 tests**, seven live searches and 17 raw response
pages at the previous checkpoint; stable Choi candidate IDs on repeated search.
See [discovery validation](records/discovery-validation.json). Initial search
profiles cover A0/A1, although pinned context can address all 32 registered RQs.
Current session: **58 tests passed**, 15 pinned Ravel blobs verified, 19 cached
source hashes matched, prior reading record preserved byte-for-byte and all root/docs
local links checked. [Validation receipt](records/pilot-review-validation-20261011.json).
No biological rerun was needed for this documentation and evidence update.
