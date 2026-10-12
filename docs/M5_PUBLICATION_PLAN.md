# M5: complete Choi output publication

**12 October 2026: owner-approved publication, independent public recovery and
clean-checkout CI qualification passed.** [Ravel PR #149](https://github.com/xorca0711/ravel/pull/149)
is ready for review at `4e44db497c72f64056688b78d828a47695384db4`; all four push/PR
checks passed. Human scientific disposition and integration remain open. Choi is
separate from B4 and the numerical analysis was not rerun.

[Publication and CI record](../records/choi-publication-20261012.json) ·
[Public evidence release](https://github.com/xorca0711/ravel/releases/tag/choi-p001-figure1-v1).
The local-candidate record below preserves the earlier preparation checkpoint.

## Prepared candidate

| Item | Verified value |
|---|---|
| Proposed destination | Public release asset in `xorca0711/ravel` |
| Proposed tag | `choi-p001-figure1-v1`, pinned to reviewed Ravel source `714945697b007f4a0046834b34251392c1cfbe5a` |
| Proposed release title | Choi P001: descriptive Figure 1 evidence, v1 |
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

## Recommended route and decision

Use a versioned **GitHub Release asset**, then restore it into its original paths
before the unchanged Ravel receipt validator runs. GitHub documents a limit of
less than 2 GiB per release asset and no aggregate release-size or bandwidth cap;
the proposed ZIP fits. See [GitHub release storage documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases#storage-and-bandwidth-quotas).
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
**Remaining human decision:** retain the bounded descriptive discrepancy record
and review/integrate Ravel #149. Neither publication nor CI records scientific
acceptance. The private coordinator reservation remains held.

## Integration sequence — publication/restoration complete; review remains

Steps 1–4 below were implemented and qualified in Ravel #149, with the unchanged
receipt validator and four passing clean-checkout CI runs. Steps 5–6 remain the
review/coordination boundary; no new scientific job is authorized.

1. Recheck GitHub identity `xorca0711`, target repository, tag absence, original
   receipt/source hashes and the selected package hash. Create a draft release
   with the pinned tag and explicit descriptive-only limitations; upload only
   this reviewed ZIP. Verify GitHub's downloaded bytes before publishing it.
2. Publish the prerelease and independently download it without relying on the
   local archive. Record release/asset IDs, resolved source revision, size and
   SHA-256. Fail on a mismatch; never silently replace a published version.
3. In a separate Ravel PR #149 change, add a narrow restoration step and checked-in
   asset lock. Bound download size, pin SHA-256, reject unsafe/duplicate ZIP paths,
   require the exact member inventory and preserve existing files on disagreement.
   Extract only original declared output paths. Do not use this as an arbitrary
   archive downloader or execute archive contents.
4. Register the **unchanged** receipt only with all 15 outputs present. Update the
   Ravel infrastructure inventory for the restoration mechanism and obtain
   explicit review of that CI addition; do not change validator semantics.
   Validate a clean clone against current Ravel main, including mismatch, missing
   member and path traversal rejection tests. Keep source/contract/output bytes
   and original unfavorable findings unchanged.
5. Present the complete Ravel change for human review. Record the human scientific
   disposition separately from engineering integration or merge. Preserve the
   current no-new-RQ recommendation and all annotation/denominator limitations.
6. Reconcile the same private Choi coordinator against the review/publication
   evidence before any new job or reservation transition. Preserve checkpoint
   ancestry and produce a verified backup through the existing approved route;
   obtain exact-payload export authority where needed.

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
