# Final Comparison Sheet - M1

## Branch snapshot

- Owner: `M1`
- Branch: `battle/m1-full-pipeline`
- Current branch theme: `lexical_semantic_blend`
- Current comparison status: `phase7_winner_ready_for_showdown`

## Executive decision

- **Main candidate to send into branch showdown:** `exp_m1_019` (`phase7_modernbert_sparse_blend`)
- **Primary lexical backup:** `exp_m1_014` (`phase4_text_only_ensemble`)
- **Semantic reserve:** `exp_m1_018` (`phase7_structured_modernbert_encoder`)
- **Legacy single-model reference:** `exp_m1_002` (`phase3_best_single_model`)

## Why M1 is more competitive now

- M1 no longer relies only on lexical n-grams. The branch now combines:
  - exact sparse text matching from the proven phase-4 ensemble
  - semantic compression from `ModernBERT` embeddings
- The new winner is not a cosmetic upgrade. It improves M1 from `0.337629` to `0.355191` on the shared CV rule.
- The semantic upgrade is still reproducible on a CPU-only machine, which matters for branch battle and final report credibility.

## Progress timeline

| Stage | Run ID | Direction | CV Macro F1 | Std | Key takeaway |
| --- | --- | --- | ---: | ---: | --- |
| Phase 2 | exp_m1_001 | text baseline | 0.327027 | 0.032543 | first clean end-to-end pipeline |
| Phase 3 | exp_m1_002 | text_tuned_binary | 0.334261 | 0.041403 | binary word representation beats standard TF-IDF |
| Phase 4 | exp_m1_014 | text_only_ensemble | 0.337629 | 0.024355 | lexical ensemble becomes branch winner |
| Phase 5 | exp_m1_014 | error-analysis validation | 0.340033 | - | ensemble remains justified after case-level inspection |
| Phase 7 | exp_m1_019 | modernbert_sparse_blend | 0.355191 | 0.032478 | lexical + semantic blend becomes new M1 winner |

## Candidate board for showdown

| Rank | Role | Run ID | Model | CV Macro F1 | Std | OOF Macro F1 | Submission | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 1 | main_candidate | exp_m1_019 | modernbert_logreg_blend | 0.355191 | 0.032478 |  | sub_m1_v4_phase7_modernbert_blend.csv | primary |
| 2 | lexical_backup | exp_m1_014 | probability_blend | 0.337629 | 0.024355 | 0.340033 | sub_m1_v3_phase4_text_ensemble.csv | backup |
| 3 | semantic_reserve | exp_m1_018 | modernbert_logistic_regression | 0.343358 | 0.060626 |  | not_submitted_yet | reserve |
| 4 | runner_up_blend | exp_m1_020 | modernbert_logreg_blend | 0.354020 | 0.041322 |  | not_submitted_yet | reserve |
| 5 | legacy_single_model | exp_m1_002 | ovr_logistic_regression | 0.334261 | 0.041403 | 0.337404 | sub_m1_v2_phase3_best.csv | reference |

## Main candidate profile

- Run ID: `exp_m1_019`
- Submission file: `sub_m1_v4_phase7_modernbert_blend.csv`
- CV Macro F1: `0.355191`
- CV std: `0.032478`
- Reason to keep: highest current CV ceiling of M1 after adding semantic transformer signal
- Main strength: captures both lexical precision and semantic similarity
- Main risk: variance is higher than the pure lexical fallback, so Kaggle still needs to confirm the gain

## Lexical backup profile

- Run ID: `exp_m1_014`
- Submission file: `sub_m1_v3_phase4_text_ensemble.csv`
- CV Macro F1: `0.337629`
- CV std: `0.024355`
- Reason to keep: already battle-tested, lower variance, and easier to defend if leaderboard dislikes the semantic blend
- Main strength: safest fallback with strong reproducibility story
- Main risk: lower ceiling than the phase-7 winner

## Semantic reserve profile

- Run ID: `exp_m1_018`
- CV Macro F1: `0.343358`
- CV std: `0.060626`
- Reason to keep: strongest standalone transformer-style encoder candidate
- Main strength: pure semantic signal, useful if the blend behaves oddly on Kaggle
- Main risk: high variance and not yet submitted

## Evidence that changed the branch direction

- User feedback on Kaggle showed the TF-IDF-only family was still too weak in leaderboard terms.
- `ModernBERT` with structured text (`title + venue + year + authors`) beat title-only encoder input clearly.
- The strongest result came from **blending** sparse and semantic probabilities, not from replacing the old model family outright.
- This suggests M1’s weakness was not that sparse text was useless; it was that lexical matching alone was leaving semantic recall on the table.

## What to compare when M1 faces other branches

1. `Public LB` of `sub_m1_v4_phase7_modernbert_blend.csv` first.
2. If Public LB is close, compare `CV Macro F1` and the gap versus the previous M1 winner.
3. If still close, compare reproducibility:
   - M1 now has a clear story from baseline -> lexical ensemble -> semantic upgrade.
4. If another branch wins on LB but is unstable or hard to reproduce, M1 should still be treated as a very strong fallback.

## Current M1 recommendation

- Submit and defend `sub_m1_v4_phase7_modernbert_blend.csv` as the main M1 candidate.
- Keep `sub_m1_v3_phase4_text_ensemble.csv` available as the lexical fallback.
- Keep `exp_m1_018` as the semantic reserve if Kaggle later disagrees with the blend.
