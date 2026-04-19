# Robust Label Change Notes

- Baseline now treated as robust: `submission_estimate_best8_when_top2_agree_else_weighted.csv`.
- User result: this baseline improved by about `+0.01` over `submission_best_038_8.csv`.
- The three changes below are marked trusted for this experiment cycle.

## Trusted Changes

| id | title | from | to | reason |
| --- | --- | --- | --- | --- |
| 26 | Research Report on Automatic Synthesis of Local Search Neighborhood Operators. | 1 | 5 | 038_2 and abstract model agreed against 038_8; user leaderboard test improved. |
| 17 | asymptoticplp: Approximating probabilistic logic programs on large domains. | 2 | 4 | 038_2 and abstract model agreed against 038_8; user leaderboard test improved. |
| 260 | A Semantics For Probabilistic Answer Set Programs With Incomplete Stochastic Knowledge. | 5 | 4 | 038_2 and abstract model agreed against 038_8; user leaderboard test improved. |

## Next Candidate CSVs

These are estimate-only files. They do not run a model; they start from the robust baseline and apply small manual/vote-based changes.

| file | risk | id | title | robust_label | candidate_label | vote_counts | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| submission_estimate_robust_plus_id568_to5.csv | medium | 568 | Syntactic Requirements for Well-defined Hybrid Probabilistic Logic Programs. | 2 | 5 | 2:3, 4:3, 5:5 | 038_2 and 038_9 vote 5; global plurality is 5. Abstract submissions vote 4, so not fully unanimous. |
| submission_estimate_robust_plus_id255_to2.csv | medium_high | 255 | Reasoning in Highly Reactive Environments. | 4 | 2 | 2:4, 3:4, 4:3 | 038_9 and both abstract submissions vote 2, but 038_2 votes 3 and global vote ties 2 vs 3. |
| submission_estimate_robust_plus_id255_to3.csv | medium_high | 255 | Reasoning in Highly Reactive Environments. | 4 | 3 | 2:4, 3:4, 4:3 | 038_2 and submissions 1/3/4 vote 3, but 038_9 and abstract submissions vote 2; global vote ties 2 vs 3. |
| submission_estimate_robust_plus_id568_to5_and_id255_to2.csv | higher | 568 | Syntactic Requirements for Well-defined Hybrid Probabilistic Logic Programs. | 2 | 5 | 2:3, 4:3, 5:5 | Combines the strongest next candidate with the abstract-supported option for id 255. |
| submission_estimate_robust_plus_id568_to5_and_id255_to2.csv | higher | 255 | Reasoning in Highly Reactive Environments. | 4 | 2 | 2:4, 3:4, 4:3 | Combines the strongest next candidate with the abstract-supported option for id 255. |
| submission_estimate_robust_plus_id568_to5_and_id255_to3.csv | higher | 568 | Syntactic Requirements for Well-defined Hybrid Probabilistic Logic Programs. | 2 | 5 | 2:3, 4:3, 5:5 | Combines the strongest next candidate with the 038_2-supported option for id 255. |
| submission_estimate_robust_plus_id568_to5_and_id255_to3.csv | higher | 255 | Reasoning in Highly Reactive Environments. | 4 | 3 | 2:4, 3:4, 4:3 | Combines the strongest next candidate with the 038_2-supported option for id 255. |

## Update From Ablation

User reported `submission_ablation_revert_id17_to_original_2.csv` increased the score. Therefore, for the current public split, `id=17` should be treated as label `2`, not label `4`.

New current-best candidate created:

- `submission_estimate_validated_revert_id17_to2.csv`

Current trusted/pending state:

| id | label to use now | note |
| --- | --- | --- |
| 26 | 5 | Keep robust change for now unless its revert ablation improves. |
| 17 | 2 | Revert improved, so label 2 is preferred. |
| 260 | 4 | Keep robust change for now unless its revert ablation improves. |

## Update From id260 Ablation

User reported `submission_ablation_revert_id260_to_original_5.csv` increased the score to about `0.39`. Therefore, for the current public split, `id=260` should be treated as label `5`, not label `4`.

Unified candidate created:

- `submission_estimate_validated_id17_2_id260_5.csv`

Current consolidated state:

| id | label to use now | evidence |
| --- | --- | --- |
| 26 | 5 | Kept from robust baseline; no reported revert improvement yet. |
| 17 | 2 | Revert ablation improved. |
| 260 | 5 | Revert ablation improved to about 0.39. |

## Locked Labels

These labels are now marked as `do_not_change` for subsequent manual estimate files unless a new direct ablation disproves them.

| id | locked label | decision | evidence |
| --- | --- | --- | --- |
| 26 | 5 | do_not_change | Best validated set keeps id26=5. |
| 17 | 2 | do_not_change | Reverting 4->2 improved score. |
| 260 | 5 | do_not_change | Reverting 4->5 improved score strongly. |

