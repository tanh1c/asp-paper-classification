# Phase 5 Error Analysis - M1

## Models compared

- Reference single model: `exp_m1_002` (`word12_binary_c6`)
- Current winner ensemble: `exp_m1_014` (`ens_best_backup_50_50`)
- Analysis method: out-of-fold predictions on the shared `StratifiedKFold(5, shuffle=True, random_state=42)`

## Important note about metrics

- Model selection for the branch still uses **mean fold Macro F1**.
- Error analysis below uses **aggregated out-of-fold predictions** so that every training sample has one fair held-out prediction and can be inspected case-by-case.
- Vì vậy, OOF Macro F1 trong report này có thể lệch nhẹ so với mean fold CV đã ghi ở tracker.

## Fold-level selection metrics

- Phase 3 single model mean fold CV: `0.334261` with std `0.041403`
- Phase 4 ensemble mean fold CV: `0.337629` with std `0.024355`

## OOF diagnostic metrics

- Phase 3 single OOF Macro F1: `0.337404`
- Phase 4 ensemble OOF Macro F1: `0.340033`

## Per-class F1 comparison

| Label | Single F1 | Ensemble F1 | Delta |
| --- | --- | --- | --- |
| 1 | 0.501901 | 0.526316 | +0.024415 |
| 2 | 0.320000 | 0.316832 | -0.003168 |
| 3 | 0.187500 | 0.184049 | -0.003451 |
| 4 | 0.192771 | 0.202381 | +0.009610 |
| 5 | 0.484848 | 0.470588 | -0.014260 |

## Error bucket counts

- `both_correct`: 169
- `fixed_by_ensemble`: 17
- `hurt_by_ensemble`: 16
- `both_wrong`: 308

## Case distribution by true label

| Label | Both Correct | Fixed by Ensemble | Hurt by Ensemble | Both Wrong |
| --- | --- | --- | --- | --- |
| 1 | 63 | 7 | 3 | 57 |
| 2 | 28 | 4 | 4 | 67 |
| 3 | 13 | 2 | 2 | 68 |
| 4 | 14 | 3 | 2 | 70 |
| 5 | 51 | 1 | 5 | 46 |

## Title and data-quality summary by case type

| Case Type | Avg Title Length | Avg Title Words | Avg Missing Authors |
| --- | --- | --- | --- |
| both_correct | 80.041 | 10.254 | 0.148 |
| both_wrong | 66.312 | 8.406 | 0.071 |
| fixed_by_ensemble | 63.471 | 7.824 | 0.235 |
| hurt_by_ensemble | 66.375 | 8.062 | 0.062 |

## Strongest confusion pairs - single model

| Count | True Label | Pred Label |
| --- | --- | --- |
| 31 | 1 | 2 |
| 28 | 4 | 5 |
| 28 | 2 | 1 |
| 21 | 3 | 5 |
| 19 | 5 | 4 |

## Strongest confusion pairs - ensemble

| Count | True Label | Pred Label |
| --- | --- | --- |
| 28 | 4 | 5 |
| 28 | 2 | 1 |
| 28 | 1 | 2 |
| 21 | 5 | 4 |
| 19 | 3 | 4 |

## Representative cases fixed by ensemble

| ID | True | Single | Ensemble | Title |
| --- | --- | --- | --- | --- |
| 518 | 2 | 1 | 2 | Action Languages and COVID-19: Lessons Learned. |
| 13 | 4 | 5 | 4 | Relational Graph Convolutional Networks Do Not Learn Sound Rules. |
| 404 | 3 | 5 | 3 | Contracted Temporal Equilibrium Logic. |
| 3 | 1 | 2 | 1 | Cumulative Scoring-Based Induction of Default Theories. |
| 365 | 4 | 1 | 4 | Recursive Aggregates as Intensional Functions. |

## Representative cases hurt by ensemble

| ID | True | Single | Ensemble | Title |
| --- | --- | --- | --- | --- |
| 136 | 5 | 5 | 3 | Probabilistic Active Goal Recognition. |
| 54 | 2 | 2 | 4 | A Comparative Study of Text Representations for French Real-Estate Classified Advertisements Information Extraction. |
| 583 | 2 | 2 | 4 | Two-Variable Logic for Hierarchically Partitioned and Ordered Data. |
| 200 | 3 | 3 | 1 | Visualizing Kripke Models in LogiKEy: the Case of SDL. |
| 434 | 4 | 4 | 2 | Neuro-Symbolic Agent with ASP for Robust Exception Learning in Text-Based Games. |

## Representative hard cases where both are wrong

| ID | True | Single | Ensemble | Title |
| --- | --- | --- | --- | --- |
| 299 | 1 | 4 | 4 | Tabled CLP for Reasoning Over Stream Data. |
| 41 | 1 | 2 | 2 | Heuristic Strategies for Accelerating Multi-Agent Epistemic Planning. |
| 403 | 4 | 1 | 1 | Flexible, Lifelong, Explainable, and Robust Solutions for Multi-Agent Path Finding Problems. |
| 569 | 1 | 2 | 2 | Planning Domain Model Acquisition from State Traces without Action Parameters. |
| 451 | 4 | 2 | 2 | On Simple Expectations and Observations of Intelligent Agents: A Complexity Study. |

## Main findings

- Ensemble improves the branch overall because it trades a small number of regressions for slightly more fixes and, importantly, a more stable behavior across folds.
- The clearest gains are on **Label 1** and **Label 4**. Label 1 F1 rises noticeably, and Label 4 also improves a bit.
- The main trade-off is **Label 5**, where the ensemble loses some recall/F1 compared with the single model.
- Labels **3** and **4** remain the hardest classes overall; even with the ensemble, their F1 is still much lower than Labels 1 and 5.
- The biggest persistent confusion zones are still around:
  - `1 -> 2`
  - `2 -> 1`
  - `4 -> 5`
  - `3 -> 4`
- Cases fixed by the ensemble tend to have slightly shorter titles and a higher share of missing authors, which suggests the second model is adding a different bias/decision boundary that helps on thinner-text cases.

## Recommendation for M1

- Keep `exp_m1_014` as the main candidate because it is better at the branch objective: stronger mean fold CV and lower variance.
- Keep `exp_m1_002` as the single-model fallback because it is still competitive and slightly better on some Label 5 cases.
- If another phase is run, focus on reducing confusion between:
  - Label 1 vs Label 2
  - Label 4 vs Label 5
  - Label 3 vs Label 4 / Label 5
