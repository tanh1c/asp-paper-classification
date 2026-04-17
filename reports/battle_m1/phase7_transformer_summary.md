# Phase 7 ModernBERT Upgrade Summary - M1

## Branch info

- Owner: M1
- Branch: `battle/m1-full-pipeline`
- Goal of this phase: push M1 beyond sparse text baselines with a modern transformer encoder
- Encoder family used: `ModernBERT`
- Encoder checkpoint: `nomic-ai/modernbert-embed-base`

## Why this phase was designed this way

- User feedback from Kaggle was clear: M1 needed a less thô sơ text method than TF-IDF-only baselines.
- The current machine is CPU-only, so a frozen encoder plus linear head was the fastest reliable way to test transformer signal at competition speed.
- Instead of replacing the sparse winner blindly, this phase tests whether a semantic encoder can **complement** the lexical n-gram ensemble that already works well.

## Phase-4 reference

- Run ID: `exp_m1_014`
- Candidate: `phase4_text_only_ensemble`
- CV Macro F1: `0.337629`
- CV std: `0.024355`

## Top phase-7 candidates

| Candidate | Group | Text Variant | C | ModernBERT Weight | CV Macro F1 | Std |
|---|---|---|---:|---:|---:|---:|
| phase4_modernbert_structured_c2_0_w0_56 | lexical_semantic_blend | structured | 2.00 | 0.56 | 0.355191 | 0.032478 |
| phase4_modernbert_structured_c3_5_w0_55 | lexical_semantic_blend | structured | 3.50 | 0.55 | 0.354020 | 0.041322 |
| phase4_modernbert_structured_c3_5_w0_56 | lexical_semantic_blend | structured | 3.50 | 0.56 | 0.353047 | 0.039526 |
| phase4_modernbert_structured_c3_0_w0_55 | lexical_semantic_blend | structured | 3.00 | 0.55 | 0.351895 | 0.039190 |
| phase4_modernbert_structured_c3_5_w0_54 | lexical_semantic_blend | structured | 3.50 | 0.54 | 0.351578 | 0.043225 |
| phase4_modernbert_structured_c3_0_w0_56 | lexical_semantic_blend | structured | 3.00 | 0.56 | 0.351371 | 0.044214 |
| phase4_modernbert_structured_c1_5_w0_6 | lexical_semantic_blend | structured | 1.50 | 0.60 | 0.351272 | 0.042456 |
| phase4_modernbert_structured_c2_5_w0_58 | lexical_semantic_blend | structured | 2.50 | 0.58 | 0.351138 | 0.044291 |
| phase4_modernbert_structured_c2_0_w0_55 | lexical_semantic_blend | structured | 2.00 | 0.55 | 0.351051 | 0.034864 |
| phase4_modernbert_structured_c3_5_w0_52 | lexical_semantic_blend | structured | 3.50 | 0.52 | 0.350937 | 0.036624 |

## Winner of Phase 7

- Candidate key: `phase4_modernbert_structured_c2_0_w0_56`
- Group: `lexical_semantic_blend`
- Text variant: `structured`
- ModernBERT logistic `C`: `2.00`
- Blend weights:
  - sparse phase-4 ensemble: `0.44`
  - ModernBERT encoder model: `0.56`
- CV Macro F1: `0.355191`
- CV std: `0.032478`

## Comparison with previous M1 winner

- Phase-4 best CV: `0.337629`
- Phase-7 best CV: `0.355191`
- Absolute improvement: `0.017562`

## Interpretation

- Pure ModernBERT encoder features already become competitive on this dataset, especially when the input text includes `title + venue + year + authors`.
- The strongest result does **not** come from throwing away sparse features. It comes from blending:
  - lexical precision from the phase-4 TF-IDF ensemble
  - semantic compression from ModernBERT embeddings
- This is exactly the kind of complementarity we want for a small competition dataset: one model catches exact n-grams, the other smooths over wording variation and topic similarity.

## Submission

- New file: `C:/Users/LG/Desktop/Study Material/DataMining/data/submissions/sub_m1_v4_phase7_modernbert_blend.csv`

## Recommendation

- Replace the old M1 main candidate with this phase-7 ModernBERT blend.
- Keep the old phase-4 ensemble as a lexical fallback.
- Keep the best standalone structured ModernBERT encoder as a semantic backup if Kaggle later disagrees with the blend.
