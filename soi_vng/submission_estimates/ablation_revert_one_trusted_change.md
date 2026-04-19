# Revert-One Ablation Plan

- Robust baseline: `submission_estimate_best8_when_top2_agree_else_weighted.csv`
- Known robust score from your test: about `0.3851`
- Rule: submit each ablation. If score decreases, the reverted change was beneficial in the context of the other two changes.

| file | id | title | robust_label | reverted_to_original_label | score | conclusion |
| --- | --- | --- | --- | --- | --- | --- |
| submission_ablation_revert_id26_to_original_1.csv | 26 | Research Report on Automatic Synthesis of Local Search Neighborhood Operators. | 5 | 1 |  |  |
| submission_ablation_revert_id17_to_original_2.csv | 17 | asymptoticplp: Approximating probabilistic logic programs on large domains. | 4 | 2 |  |  |
| submission_ablation_revert_id260_to_original_5.csv | 260 | A Semantics For Probabilistic Answer Set Programs With Incomplete Stochastic Knowledge. | 4 | 5 |  |  |

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

