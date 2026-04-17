# Final Comparison Sheet - M1

## Branch snapshot

- Owner: `M1`
- Branch: `battle/m1-full-pipeline`
- Current branch theme: `text_only_ensemble`
- Current comparison status: `ready_for_branch_showdown`

## Executive decision

- **Main candidate to send into branch showdown:** `exp_m1_014` (`phase4_text_only_ensemble`)
- **Primary backup:** `exp_m1_002` (`phase3_best_single_model`)
- **Stability reserve:** `exp_m1_011` (`phase3_stability_backup`)

## Why M1 is competitive

- M1 found a clean progression from baseline -> tuned single model -> text-only ensemble, instead of jumping into unnecessary hybrid complexity.
- The current winner `exp_m1_014` is not only the best CV candidate of M1, but also more stable than the best single model.
- Error analysis shows the ensemble improves the branch in a real way, especially on Label 1 and Label 4, not just by random fold noise.

## Progress timeline

| Stage | Run ID | Direction | CV Macro F1 | Std | Key takeaway |
| --- | --- | --- | --- | --- | --- |
| Phase 2 | exp_m1_001 | text baseline | 0.327027 | 0.032543 | first clean end-to-end pipeline |
| Phase 3 | exp_m1_002 | text_tuned_binary | 0.334261 | 0.041403 | binary word representation beats standard TF-IDF |
| Phase 4 | exp_m1_014 | text_only_ensemble | 0.337629 | 0.024355 | text-only ensemble becomes branch winner |
| Phase 5 | exp_m1_014 | error-analysis validation | 0.340033 | - | ensemble remains justified after case-level inspection |

## Candidate board for showdown

| Rank | Role | Run ID | Model | CV Macro F1 | Std | OOF Macro F1 | Submission | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | main_candidate | exp_m1_014 | probability_blend | 0.337629 | 0.024355 | 0.340033 | sub_m1_v3_phase4_text_ensemble.csv | primary |
| 2 | single_model_backup | exp_m1_002 | ovr_logistic_regression | 0.334261 | 0.041403 | 0.337404 | sub_m1_v2_phase3_best.csv | backup |
| 3 | stability_backup | exp_m1_011 | ovr_logistic_regression | 0.330420 | 0.023573 |  | not_submitted_yet | reserve |
| 4 | baseline_reference | exp_m1_001 | ovr_logistic_regression | 0.327027 | 0.032543 |  | sub_m1_v1_text_word12_ovr_lr.csv | reference |

## Main candidate profile

- Run ID: `exp_m1_014`
- Submission file: `sub_m1_v3_phase4_text_ensemble.csv`
- CV Macro F1: `0.337629`
- CV std: `0.024355`
- Reason to keep: best mean CV and much lower variance than the best single model
- Main strength: strongest overall branch candidate
- Main risk: slight trade-off on Label 5

## Backup candidate profile

- Run ID: `exp_m1_002`
- Submission file: `sub_m1_v2_phase3_best.csv`
- CV Macro F1: `0.334261`
- CV std: `0.041403`
- Reason to keep: best explainable single model and still competitive
- Main strength: good single-model reference, useful if leaderboard dislikes ensemble bias
- Main risk: higher variance than the ensemble winner

## Stability reserve profile

- Run ID: `exp_m1_011`
- CV Macro F1: `0.330420`
- CV std: `0.023573`
- Reason to keep: not the highest mean, but very stable and helped build the phase-4 winner
- Main strength: lowest variance among serious candidates
- Main risk: not yet submitted and lower mean than main/backup

## Evidence from error analysis

- Ensemble OOF Macro F1: `0.340033`
- Single-model OOF Macro F1: `0.337404`
- Fixed by ensemble: `17`
- Hurt by ensemble: `16`
- Hardest labels still left: `3, 4`
- Biggest gains:
  - Label 1 F1 delta: `+0.024415`
  - Label 4 F1 delta: `+0.009610`
- Main trade-off:
  - Label 5 F1 delta: `-0.014260`

## What to compare when M1 faces other branches

1. `Public LB` of `sub_m1_v3_phase4_text_ensemble.csv` first.
2. If Public LB is close, compare `CV Macro F1` and `std`.
3. If still close, compare explainability:
   - M1 has a very clean story from baseline to tuned text-only ensemble.
4. If another branch wins on LB but is unstable or hard to reproduce, M1 should still be considered a serious fallback.

## Current M1 recommendation

- Submit and defend `sub_m1_v3_phase4_text_ensemble.csv` as the main M1 candidate.
- Keep `sub_m1_v2_phase3_best.csv` available as the single-model fallback.
- Use `exp_m1_011` as the stability reference when discussing variance and why the final ensemble is constructed the way it is.
