# M5: complete Choi output publication

**12 October 2026: M5 complete for the bounded Choi descriptive benchmark.**
The owner approved publication, retained the descriptive discrepancy result and
authorized integration. [Ravel PR #149](https://github.com/xorca0711/ravel/pull/149)
merged at `34675134a5581989d028102a93ae51eebc84a501`; both main CI workflows
passed. No new RQ, causal claim or claim-grade promotion was approved. Choi
remains separate from held B4; no numerical analysis reran.

[Publication and CI record](../records/choi-publication-20261012.json) ·
[Public evidence release](https://github.com/xorca0711/ravel/releases/tag/choi-p001-figure1-v1).
The local-candidate record below preserves the earlier preparation checkpoint.

## Published package

| Item | Verified value |
|---|---|
| Destination | Public release asset in `xorca0711/ravel` |
| Tag | `choi-p001-figure1-v1`, pinned to reviewed Ravel source `714945697b007f4a0046834b34251392c1cfbe5a` |
| Release title | Choi P001: descriptive Figure 1 evidence, v1 |
| Release classification | Prerelease evidence package; not a validated biological reproduction |
| Asset | `choi-p001-figure1-v1-complete-outputs.zip` |
| Compressed bytes | 105,582,086 |
| Asset SHA-256 | `6e10afc432fdffb32ece7a3692c8dbb302c74604e9e67e27793c8d1856de21e2` |
| Contents | All 15 original outputs, unchanged original receipt, publication manifest: 17 ZIP members |
| Largest output | H5AD, 385,675,968 bytes |
| Original receipt SHA-256 | `24aaaaef907519391ba3c8650f96795ebe2dff4a27cd4ad9e9977852cdc5974b` |

The [candidate inventory](../records/choi-publication-candidate-20261012.json)
records every member's original path, length and digest. The package retains
repository-relative run identifiers already present in public provenance.
It excludes the private recovery archive's coordinator databases, Drive locators,
worker/session records, checkpoints, source downloads and execution logs.

All declared output hashes and the original receipt hash match. ZIP CRC and
17-member inventory checks passed. A fresh local staging root containing the
unchanged receipt, outputs, contract and hash-bound source files passed Ravel's
existing `research_gate.py verify` with zero errors. This establishes local
byte/receipt compatibility, **not remote availability or clean-clone CI**.

Review inspected all JSON/CSV text, metadata in all five PNGs, and all HDF5 string
datasets/attributes: 40,426 string values, 82 HDF5 datasets and 246 attributes.
No credential, email, private absolute-path or private-service-link pattern
matches remained. The first scanner pass incorrectly matched the `s:/` in the
public Matplotlib HTTPS URL; the drive-path boundary was corrected after checking
the five exact values. Original files were not edited. Prior visual review of all
five figures is reused. Pattern/metadata inspection is not an exhaustive privacy
proof and did not use image OCR.

## Qualified route and owner decision

Use a versioned **GitHub Release asset**, then restore it into its original paths
before the unchanged Ravel receipt validator runs. GitHub documents a limit of
less than 2 GiB per release asset and no aggregate release-size or bandwidth cap;
the published ZIP fits. See [GitHub release storage documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases#storage-and-bandwidth-quotas).
The route uses the existing repository/account rather than a new paid storage
service. It does not add the H5AD to ordinary Git history or enable Git LFS.

**Owner decision recorded:** publish this exact package publicly in Ravel and
qualify its download/CI restoration. The named package, byte size and SHA-256
were explicitly approved. Release `410591160`, asset `633765798`, draft readback
and unauthenticated public recovery are verified. The tag resolves to the reviewed
source above. PR #149 registers the original receipt and restores all outputs
before the unchanged validators; its clean-checkout CI passed.

The first CI run correctly rejected a comment-only `.gitignore` change because
the file is frozen source provenance. Exact original bytes were restored, with
no validator or contract change. The corrected head passed all checks.
The owner subsequently retained the bounded descriptive discrepancy benchmark
and approved Ravel #149 / Weft #9 integration. Ravel #149 merged and its two main
checks passed. The [human disposition](https://github.com/xorca0711/ravel/blob/main/Research%20Article/gate1_02_choi_2020/weft_pilot_v1/REVIEW_DISPOSITION.md)
is separate from successful publication or CI. The private coordinator reservation
remains held; this closeout did not mutate the ledger.

## Completed integration and remaining operational boundary

1. Verified the external-service identity, pinned source, original receipt and
   exact approved archive; uploaded to a draft release and verified readback.
2. Published the prerelease and independently recovered its public bytes.
3. Added the bounded, hash-locked restorer and rejection/preservation tests.
4. Registered the unchanged receipt with all 15 outputs recoverable; qualified
   both clean-checkout CI workflows without changing validator semantics.
5. Recorded the owner's bounded retention, merged Ravel #149 and verified main CI.

Before any future job or reservation transition, reconcile the same private Choi
coordinator with this publication and human disposition, preserve checkpoint
ancestry and verify any authorized backup. This is an operational prerequisite
for a later job, not permission to rerun the completed benchmark.

The owner requested migration of the scientific trial dossier into Ravel's
`weft_intake/choi-2020-p001/v1/`. Weft retains automation/deployment records and
historical receipts; the intake collects source review, input inventories and
scientific interpretation without moving existing frozen Ravel outputs.

## After M5

M5 does not unblock B4 or qualify unattended scientific operation. B4 stays held
pending platform resolution; no new worker or alternate route is authorized.
The next backend work is B5's independent evaluation design and software-only
launcher/recovery qualification. Freeze evaluation sampling, independent human
labels and pass/fail criteria before claiming unseen-paper accuracy. Choi and the
already exposed development candidates cannot serve as unseen evaluation data.

M6 stays disabled until independent evaluation, a supported unattended execution
route and owner-selected cadence, query scope and usage limits are resolved.
No schedule, paid execution, new privileges or automatic claim admission follows
from merging PRs #4–#8. See the [marked roadmap](IMPLEMENTATION_PLAN.md#established-state).
