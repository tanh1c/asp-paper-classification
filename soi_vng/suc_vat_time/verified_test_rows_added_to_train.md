# Verified Test Rows Added To Train

- Output augmented train: `soi_vng/Stage_1_publcitrain_with_abstract_plus_verified_test.csv`
- Added/verified/pseudo-labeled test rows currently tracked: `39`
- Augmented train rows: `549`

Use this as pseudo-labeled/verified augmentation. It may improve public leaderboard robustness, but it can overfit public feedback/private split.

| id | title | doi | Label | review_status | reason |
| --- | --- | --- | --- | --- | --- |
| 2 | Finite Axiomatizability by Disjunctive Existential Rules. | 10.24963/kr.2025/20 | 1 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 7 | Integrating SMT solvers into Goal-Directed Answer Set Programming, Challenges and Directions. | 10.1017/s1471068414000118 | 5 | locked_user_verified_duplicate_doi | user_verified_duplicate_doi_group: DOI 10.1017/s1471068414000118 manually verified; keep label 5. |
| 17 | asymptoticplp: Approximating probabilistic logic programs on large domains. | 10.1017/s1471068425100161 | 2 | locked_directly_validated | direct_ablation: reverting 4->2 improved score |
| 21 | Unmanned Aerial Vehicle Compliance Checking using Goal-Directed Answer Set Programming. | 10.1017/s1471068414000118 | 5 | locked_user_verified_duplicate_doi | user_verified_duplicate_doi_group: DOI 10.1017/s1471068414000118 manually verified; keep label 5. |
| 22 | Past-present temporal programs over finite traces: a preliminary report. | 10.1007/978-3-031-43619-2_53 | 3 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 26 | Research Report on Automatic Synthesis of Local Search Neighborhood Operators. | 10.4204/eptcs.306.59 | 5 | locked_directly_validated | direct_leaderboard_inference: keep id26=5 after id17/id260 errors were isolated |
| 35 | On the Suitability of Inconsistency Measures. | 10.5220/0005824305320539 | 2 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 63 | An Embarrassingly Parallel Model Counter. | 10.24963/kr.2025/65 | 1 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 88 | Knowledge-Driven Robot Program Synthesis from Human VR Demonstrations. | 10.24963/kr.2023/4 | 2 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 101 | Formal Aspects of Strategic Reasoning. | 10.4324/9780203503881-7 | 5 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 124 | An ASP-Based Framework for MUSes. | 10.4204/eptcs.439.3 | 4 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 126 | Extended Abstract: Early Validation of High-level System Requirements with Event Calculus and Answer Set Programming. | 10.1017/s1471068424000280 | 4 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 129 | Explainability Through Argumentation in Logic Programming. | 10.1016/s0743-1066(00)00004-2 | 3 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 142 | ASP-QRAT: A Conditionally Optimal Dual Proof System for ASP. | 10.24963/kr.2024/24 | 3 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 144 | Semantic Versioning Checking in a Declarative Package Manager. | 10.1145/3479394.3479416 | 1 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 181 | Answer Set Counting and its Applications. | 10.4204/eptcs.416.34 | 5 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 210 | Information Extraction Tool Text2ALM: From Narratives to Action Language System Descriptions. | 10.3233/aic-220194 | 5 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 219 | Weighted Conditional EL⊥ Knowledge Bases with Integer Weights: an ASP Approach. | 10.4204/eptcs.345.19 | 4 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 226 | On the impact of sensors update in declarative AI for videogames. | 10.1002/seup.v12:1 | 1 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 242 | Solving B Constraints with Goal-directed Answer Set Programming. | 10.1017/s1471068414000118 | 5 | locked_user_verified_duplicate_doi | user_verified_duplicate_doi_group: DOI 10.1017/s1471068414000118 manually verified; keep label 5. |
| 255 | Reasoning in Highly Reactive Environments. | 10.4204/eptcs.306.57 | 3 | locked_user_verified | user_verified: id 255 label 3 confirmed; keep label 3. |
| 260 | A Semantics For Probabilistic Answer Set Programs With Incomplete Stochastic Knowledge. | 10.1201/9781003427421-6 | 5 | locked_directly_validated | direct_ablation: reverting 4->5 improved score strongly |
| 262 | Efficient OWL2QL Meta-reasoning Using ASP-based Hybrid Knowledge Bases. | 10.4204/eptcs.416.17 | 3 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 281 | On the Complexity of Global Necessary Reasons to Explain Classification. | 10.24963/kr.2025/21 | 5 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 293 | Extended abstract: 푓퐶퐴푆푃 - A forgetting technique for XAI based on goal-directed constraint ASP models. | 10.4204/eptcs.364.24 | 3 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 295 | Sequence Explanations for Acceptance in Abstract Argumentation. | 10.24963/kr.2025/12 | 3 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 307 | PEG 2.0: Future-Gazing Through a Socio-Linguistic and Historical Lens. | 10.1126/science.1662-b | 3 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 313 | Situation Calculus Temporally Lifted Abstractions for Generalized Planning - Extended Abstract. | 10.1609/aaai.v39i14.33628 | 1 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 315 | Unifying Abduction and Deduction through Argumentation. | 10.1093/med/9780190912925.003.0005 | 2 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 367 | Revising Weighted Knowledge Bases Using FH-Conditioning. | 10.1016/b978-1-4832-1452-8.50151-2 | 1 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 402 | Explaining Actual Causation via Reasoning About Actions and Change. | 10.17918/kp1w-ma77 | 5 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 414 | Solving Recurrence Relations using Machine Learning, with Application to Cost Analysis. | 10.4204/eptcs.385.16 | 2 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 428 | A Note on Occur-Check. | 10.4204/eptcs.345.17 | 1 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 473 | On Gradual Semantics for Assumption-Based Argumentation. | 10.24963/kr.2025/50 | 3 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 498 | Research Summary on Implementing Functional Patterns by Synthesizing Inverse Functions. | 10.4204/eptcs.325.39 | 4 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 529 | Sequent-Type Calculi for Systems of Nonmonotonic Paraconsistent Logics. | 10.4204/eptcs.325.23 | 1 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 577 | UserArmor: An extension for AppArmor. | 10.3390/a18040185 | 1 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 587 | The Impact of Structure in Answer Set Counting: Fighting Cycles and its Limits. | 10.24963/kr.2023/34 | 4 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
| 591 | Learning to Ground Existentially Quantified Goals. | 10.24963/kr.2024/80 | 5 | user_added_red_diff_to_train | user_requested_from_red_diff: add this id,label pair to augmented train. |
