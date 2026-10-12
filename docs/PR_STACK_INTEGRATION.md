# PR stack integration check

**12 October 2026: PRs #4–#8 merged in the authorized order.** Each successor
was retargeted to `main` before merging, using merge commits to preserve stack
ancestry. Every resulting `main` commit passed its new push CI before the next
merge. No admin bypass, squash, branch deletion or scientific acceptance was used.

| PR | Final target | Merge commit | Post-merge main CI |
|---|---|---|---|
| [#4](https://github.com/xorca0711/weft/pull/4) | `main` | `4a7c6f4` | [Passed](https://github.com/xorca0711/weft/actions/runs/38249721059) |
| [#5](https://github.com/xorca0711/weft/pull/5) | `main` | `7442f4c` | [Passed](https://github.com/xorca0711/weft/actions/runs/38249828097) |
| [#6](https://github.com/xorca0711/weft/pull/6) | `main` | `3d13a9b` | [Passed](https://github.com/xorca0711/weft/actions/runs/38249933938) |
| [#7](https://github.com/xorca0711/weft/pull/7) | `main` | `a05496a` | [Passed](https://github.com/xorca0711/weft/actions/runs/38250043578) |
| [#8](https://github.com/xorca0711/weft/pull/8) | `main` | `719666e` | [Passed](https://github.com/xorca0711/weft/actions/runs/38250240790) |

The [machine-readable integration record](../records/pr-stack-merged-20261012.json)
contains exact heads, merge commits and check URLs. Retargeted comparisons were
conflict-free; the final integration tree equals the reviewed PR #8 tree.
Choi's Ravel #149 was subsequently merged separately, after owner-approved
descriptive retention, public recovery and clean-checkout checks. Its main CI
passed at `34675134a5581989d028102a93ae51eebc84a501`. B4 remains on hold.
See [M5 closeout](M5_PUBLICATION_PLAN.md) for the completed bounded integration and remaining operational boundary.

## Historical pre-merge audit

**12 October 2026: no textual merge conflicts found for PRs #4-#8.** All five
were open, non-draft and `MERGEABLE` / `CLEAN` in the GitHub snapshot. Each had
both push and pull-request offline-validation checks passing. No merge,
retarget, branch deletion or review approval was performed.

## Verified stack

| Merge order | PR | Current target | Audited head | Result |
|---|---|---|---|---|
| 1 | [#4: Choi review and backend priority](https://github.com/xorca0711/weft/pull/4) | `main` | `b3a2ce1` | Clean; checks pass |
| 2 | [#5: batch coordinator and screening interface](https://github.com/xorca0711/weft/pull/5) | #4 branch | `827ad51` | Clean; checks pass |
| 3 | [#6: portable paths and cloud recovery](https://github.com/xorca0711/weft/pull/6) | #5 branch | `89b833e` | Clean; checks pass |
| 4 | [#7: B3 coverage and proposal records](https://github.com/xorca0711/weft/pull/7) | #6 branch | `d95d558` | Clean; checks pass |
| 5 | [#8: recovery, interruption and roadmap](https://github.com/xorca0711/weft/pull/8) | #7 branch | `482429b` before this documentation update | Clean; checks pass at the audited head |

The fetched `main` was `b59ed911874f869da825b94d19b59ad0544dfdd3`.
For each step, `git merge-base --is-ancestor` confirmed the preceding head is
contained in the incoming head. A cumulative `git merge-tree --write-tree`
simulation exited zero at all five steps, with no conflicts and a result equal
to each incoming tree. It changed no branch, index or working-tree files.
Later roadmap-only changes in #8 retain the same ancestry; recheck its current
CI before integration. Private command receipts are retained in the local run
directory; no cloud task identifiers or full paper materials are published here.

## Integration sequence

1. Review and merge **#4 into main** first.
2. Verify or change **#5's base to main**, inspect its diff and wait for checks
   against that base. Merge only after the normal review decision.
3. Repeat for **#6, #7 and #8**, in that order. Keep predecessor branches until
   dependent PRs have been retargeted and their comparisons verified.

Merge commits preserve the ancestry used by this audit. If squash or rebase
merges are chosen, reconcile the remaining stack before proceeding; do not
assume the same comparisons remain valid. Merging #8 into its current target
alone would only update the #7 branch, not main.

This check establishes textual integration and the recorded CI state. It is
not an independent semantic code review, scientific acceptance or authorization
to merge. B4's runtime safety hold is separate from Git mergeability. Choi's
Ravel PR #149 remains open/draft with publication and human review unfinished.
See the [marked roadmap](IMPLEMENTATION_PLAN.md#established-state) and
[current work state](../PROGRESS.md).
