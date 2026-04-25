# Conservative Label Review

This replaces the earlier overconfident interpretation. With public F1 around `0.39`, model consensus is not enough to block a label as correct.

## Counts

- Total IDs: `86`
- Locked direct/leaderboard validated: `3`
- Needs review total: `83`
- Consensus candidates but not locked: `73`
- Disagreement suspicious: `10`

## Locked Labels

| id | title | final_label | label_s8 | label_s2 | label_s9 | label_abs | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | asymptoticplp: Approximating probabilistic logic programs on large domains. | 2 | 2 | 4 | 4 | 4 | direct_ablation: reverting 4->2 improved score |
| 26 | Research Report on Automatic Synthesis of Local Search Neighborhood Operators. | 5 | 1 | 5 | 1 | 5 | direct_leaderboard_inference: keep id26=5 after id17/id260 errors were isolated |
| 260 | A Semantics For Probabilistic Answer Set Programs With Incomplete Stochastic Knowledge. | 5 | 5 | 4 | 4 | 4 | direct_ablation: reverting 4->5 improved score strongly |

## Needs Review

| id | title | final_label | label_s8 | label_s2 | label_s9 | label_abs | review_status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | Finite Axiomatizability by Disjunctive Existential Rules. | 1 | 1 | 1 | 1 | 5 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 7 | Integrating SMT solvers into Goal-Directed Answer Set Programming, Challenges and Directions. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 21 | Unmanned Aerial Vehicle Compliance Checking using Goal-Directed Answer Set Programming. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 22 | Past-present temporal programs over finite traces: a preliminary report. | 3 | 3 | 3 | 1 | 1 | suspicious_disagreement | Submissions disagree. |
| 35 | On the Suitability of Inconsistency Measures. | 2 | 2 | 2 | 2 | 2 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 45 | Speeding up Lazy-Grounding Answer Set Solving. | 4 | 4 | 4 | 4 | 1 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 51 | Penalization Framework For Autonomous Agents Using Answer Set Programming. | 4 | 4 | 4 | 4 | 2 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 59 | An Intuitionistic Version of Alternating-Time Temporal Logic. | 2 | 2 | 2 | 2 | 2 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 63 | An Embarrassingly Parallel Model Counter. | 1 | 1 | 1 | 1 | 4 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 76 | Logic Programming for XAI: A Technical Perspective. | 4 | 4 | 4 | 4 | 5 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 81 | Reasoning in Defeasible Description Logics with System W and Lexicographic Inference. | 3 | 3 | 3 | 3 | 3 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 88 | Knowledge-Driven Robot Program Synthesis from Human VR Demonstrations. | 2 | 2 | 1 | 2 | 2 | suspicious_disagreement | Submissions disagree. |
| 89 | Proceedings of the International Conference on Logic Programming 2021 Workshops co-located with the 37th International Conference on Logic Programming (ICLP 2021), Porto, Portugal (virtual), September 20th-21st, 2021. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 93 | Establish Coherence in Logic Programs Modelling Expert Knowledge via Argumentation. | 5 | 5 | 5 | 1 | 3 | suspicious_disagreement | Submissions disagree. |
| 101 | Formal Aspects of Strategic Reasoning. | 5 | 5 | 5 | 5 | 3 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 109 | A Tensor-Based Probabilistic Event Calculus. | 2 | 2 | 2 | 2 | 2 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 110 | Solving Argumentation Problems Using Answer Set Programming with Quantifiers: Preliminary Report. | 4 | 4 | 4 | 4 | 1 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 114 | Non-Rigid Designators in Modal and Temporal Free Description Logics. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 115 | Formal Verification of Answer Set Programs Containing Advanced Language Constructs. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 124 | An ASP-Based Framework for MUSes. | 4 | 4 | 4 | 4 | 5 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 126 | Extended Abstract: Early Validation of High-level System Requirements with Event Calculus and Answer Set Programming. | 4 | 4 | 4 | 4 | 4 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 129 | Explainability Through Argumentation in Logic Programming. | 3 | 3 | 3 | 3 | 4 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 140 | Putting Perspective into OWL [Sic]: Complexity-Neutral Standpoint Reasoning for Ontology Languages via Monodic S5 over Counting Two-Variable First-Order Logic. | 2 | 2 | 2 | 2 | 2 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 142 | ASP-QRAT: A Conditionally Optimal Dual Proof System for ASP. | 3 | 3 | 3 | 3 | 5 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 144 | Semantic Versioning Checking in a Declarative Package Manager. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 145 | P-rho-Log: Combining Logic Programming with Conditional Transformation Systems. | 1 | 1 | 1 | 1 | 3 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 156 | VECSR: Virtually Embodied Common Sense Reasoning System. | 3 | 3 | 3 | 5 | 5 | suspicious_disagreement | Submissions disagree. |
| 160 | Rewriting Optimization Statements in Answer-Set Programs. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 181 | Answer Set Counting and its Applications. | 5 | 5 | 5 | 5 | 4 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 185 | An ASP Framework for Efficient Urban Traffic Optimization. | 3 | 3 | 3 | 3 | 3 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 193 | A Sound and Complete Axiomatisation for Intuitionistic Linear Temporal Logic. | 2 | 2 | 2 | 2 | 2 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 205 | An application of Answer Set Programming in Distributed Architectures: ASP Microservices. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 207 | Counterfactual and Semifactual Explanations in Abstract Argumentation: Formal Foundations, Complexity and Computation. | 3 | 3 | 3 | 3 | 5 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 210 | Information Extraction Tool Text2ALM: From Narratives to Action Language System Descriptions. | 5 | 5 | 5 | 5 | 1 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 211 | VERUS-LM: a Versatile Framework for Combining LLMs with Symbolic Reasoning. | 3 | 3 | 3 | 3 | 3 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 217 | Towards Incorporating Normative Requirements In Autonomous Systems Using Datalog. | 1 | 1 | 2 | 1 | 3 | suspicious_disagreement | Submissions disagree. |
| 219 | Weighted Conditional EL⊥ Knowledge Bases with Integer Weights: an ASP Approach. | 4 | 4 | 4 | 4 | 4 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 221 | Achieving High Quality Knowledge Acquisition using Controlled Natural Language. | 4 | 4 | 4 | 4 | 4 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 226 | On the impact of sensors update in declarative AI for videogames. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 242 | Solving B Constraints with Goal-directed Answer Set Programming. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 255 | Reasoning in Highly Reactive Environments. | 4 | 4 | 3 | 2 | 2 | suspicious_disagreement | Submissions disagree. |
| 256 | ASP and PDDL+ Applications in Urban Traffic Distribution and Control. | 4 | 4 | 4 | 4 | 1 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 262 | Efficient OWL2QL Meta-reasoning Using ASP-based Hybrid Knowledge Bases. | 3 | 3 | 3 | 3 | 3 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 274 | Interactive Exploration of Plan Spaces. | 2 | 2 | 2 | 2 | 2 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 281 | On the Complexity of Global Necessary Reasons to Explain Classification. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 293 | Extended abstract: 푓퐶퐴푆푃 - A forgetting technique for XAI based on goal-directed constraint ASP models. | 3 | 3 | 3 | 3 | 3 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 294 | Logical Distillation of Graph Neural Networks. | 3 | 3 | 3 | 3 | 3 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 295 | Sequence Explanations for Acceptance in Abstract Argumentation. | 3 | 3 | 3 | 3 | 3 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 297 | Monotone Rewritability and the Analysis of Queries, Views, and Rules. | 2 | 2 | 2 | 2 | 2 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 307 | PEG 2.0: Future-Gazing Through a Socio-Linguistic and Historical Lens. | 3 | 3 | 3 | 3 | 4 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 313 | Situation Calculus Temporally Lifted Abstractions for Generalized Planning - Extended Abstract. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 315 | Unifying Abduction and Deduction through Argumentation. | 2 | 2 | 2 | 2 | 3 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 328 | On the Expressiveness of Spatial Constraint Systems. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 329 | Expanding the Class of Polynomial Time Computable Well-Founded Semantics for Hybrid MKNF. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 360 | Natural Language Question Answering with Goal-directed Answer Set Programming. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 367 | Revising Weighted Knowledge Bases Using FH-Conditioning. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 368 | A Rule-Based System for Explainable Donor-Patient Matching in Liver Transplantation. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 385 | A Compositional Typed Higher-Order Logic with Definitions. | 2 | 2 | 2 | 2 | 2 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 402 | Explaining Actual Causation via Reasoning About Actions and Change. | 5 | 5 | 4 | 5 | 3 | suspicious_disagreement | Submissions disagree. |
| 406 | Flexible and Explainable Solutions for Multi-Agent Path Finding Problems. | 4 | 4 | 4 | 4 | 4 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 411 | Epistemic Logic Programs with World View Constraints. | 2 | 2 | 2 | 2 | 2 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 414 | Solving Recurrence Relations using Machine Learning, with Application to Cost Analysis. | 2 | 2 | 2 | 2 | 1 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 418 | Proceedings 37th International Conference on Logic Programming (Technical Communications), ICLP Technical Communications 2021, Porto (virtual event), 20-27th September 2021. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 428 | A Note on Occur-Check. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 432 | A Framework for Defining Behavior Modes in Policy-Aware Autonomous Agents. | 2 | 2 | 2 | 2 | 1 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 438 | Action Model Learning with Guarantees. | 2 | 2 | 5 | 2 | 1 | suspicious_disagreement | Submissions disagree. |
| 439 | Building Health Policy Enforcement Solution Based on HL7 FHIR. | 1 | 1 | 1 | 1 | 2 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 465 | Large Neighborhood Prioritized Search for Combinatorial Optimization with Answer Set Programming. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 468 | Understanding Restaurant Stories Using an ASP Theory of Intentions. | 5 | 5 | 5 | 5 | 1 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 473 | On Gradual Semantics for Assumption-Based Argumentation. | 3 | 3 | 3 | 3 | 2 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 485 | How well do SOTA legal reasoning models support abductive reasoning? | 5 | 5 | 5 | 5 | 3 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 498 | Research Summary on Implementing Functional Patterns by Synthesizing Inverse Functions. | 4 | 4 | 4 | 4 | 4 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 509 | A Rule-Based Approach to Specifying Preferences over Conflicting Facts and Querying Inconsistent Knowledge Bases. | 5 | 5 | 4 | 5 | 3 | suspicious_disagreement | Submissions disagree. |
| 527 | Summary on &quot;Hybrid Neuro-Symbolic Approach for Text-Based Games using Inductive Logic&quot;. | 4 | 4 | 4 | 4 | 4 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 529 | Sequent-Type Calculi for Systems of Nonmonotonic Paraconsistent Logics. | 1 | 1 | 1 | 1 | 2 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 548 | Answer Set Programming for Qualitative Spatio-Temporal Reasoning: Methods and Experiments. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 562 | The Learning-Knowledge-Reasoning Paradigm for Natural Language Understanding and Question Answering. | 5 | 5 | 5 | 5 | 4 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 566 | Proceedings of the 22nd International Conference on Principles of Knowledge Representation and Reasoning, KR 2025, Melbourne, Australia, November 1-17, 2025 | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 568 | Syntactic Requirements for Well-defined Hybrid Probabilistic Logic Programs. | 2 | 2 | 5 | 5 | 4 | suspicious_disagreement | Submissions disagree. |
| 570 | Logic Programming with Max-Clique and its Application to Graph Coloring (Tool Description). | 3 | 3 | 3 | 3 | 1 | consensus_candidate_top_models_agree | Top/reference submissions agree, but this is not locked because consensus may still be wrong. |
| 577 | UserArmor: An extension for AppArmor. | 1 | 1 | 1 | 1 | 1 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 587 | The Impact of Structure in Answer Set Counting: Fighting Cycles and its Limits. | 4 | 4 | 4 | 4 | 4 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
| 591 | Learning to Ground Existentially Quantified Goals. | 5 | 5 | 5 | 5 | 5 | consensus_candidate_all_models_agree | All checked submissions agree, but this is not locked because public F1 is low. |
