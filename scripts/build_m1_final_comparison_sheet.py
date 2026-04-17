from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.paths import load_config, resolve_project_path


BRANCH_CONFIG_PATH = "configs/branches/m1_full_pipeline.yaml"


def write_text_file(path: Path, content: str) -> None:
    """Write UTF-8 text with parent creation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a simple markdown table."""
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_lines = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, separator_line, *body_lines])


def build_candidate_rows(shared_config: dict, branch_config: dict) -> pd.DataFrame:
    """Assemble the candidate board for the M1 showdown sheet."""
    tracker_df = pd.read_csv(resolve_project_path(shared_config["paths"]["experiment_tracker"]))
    submission_df = pd.read_csv(resolve_project_path(shared_config["paths"]["submission_log"]))

    phase5 = branch_config["phase_5_result"]
    showdown = branch_config["showdown_ready"]
    phase2 = branch_config["phase_2_result"]

    candidate_specs = [
        {
            "rank": 1,
            "role": "main_candidate",
            "run_id": showdown["main_run_id"],
            "submission_id": showdown["main_submission_id"],
            "candidate_name": "phase4_text_only_ensemble",
            "status": "primary",
            "reason_to_keep": "best mean CV and much lower variance than the best single model",
            "main_strength": "strongest overall branch candidate",
            "main_risk": "slight trade-off on Label 5",
            "oof_macro_f1": round(float(phase5["ensemble_oof_macro_f1"]), 6),
        },
        {
            "rank": 2,
            "role": "single_model_backup",
            "run_id": showdown["single_backup_run_id"],
            "submission_id": showdown["single_backup_submission_id"],
            "candidate_name": "phase3_best_single_model",
            "status": "backup",
            "reason_to_keep": "best explainable single model and still competitive",
            "main_strength": "good single-model reference, useful if leaderboard dislikes ensemble bias",
            "main_risk": "higher variance than the ensemble winner",
            "oof_macro_f1": round(float(phase5["single_oof_macro_f1"]), 6),
        },
        {
            "rank": 3,
            "role": "stability_backup",
            "run_id": showdown["stability_backup_run_id"],
            "submission_id": "",
            "candidate_name": "phase3_stability_backup",
            "status": "reserve",
            "reason_to_keep": "not the highest mean, but very stable and helped build the phase-4 winner",
            "main_strength": "lowest variance among serious candidates",
            "main_risk": "not yet submitted and lower mean than main/backup",
            "oof_macro_f1": "",
        },
        {
            "rank": 4,
            "role": "baseline_reference",
            "run_id": showdown["baseline_reference_run_id"],
            "submission_id": phase2.get("submission_id", "sub_m1_001"),
            "candidate_name": "phase2_baseline_reference",
            "status": "reference",
            "reason_to_keep": "clean baseline for telling the improvement story",
            "main_strength": "simple and easy to explain",
            "main_risk": "clearly weaker than later candidates",
            "oof_macro_f1": "",
        },
    ]

    rows = []
    for spec in candidate_specs:
        tracker_row = tracker_df.loc[tracker_df["run_id"] == spec["run_id"]].iloc[0]
        submission_match = (
            submission_df.loc[submission_df["submission_id"] == spec["submission_id"]]
            if spec["submission_id"]
            else pd.DataFrame()
        )
        if not submission_match.empty:
            submission_row = submission_match.iloc[0]
            submission_file = submission_row["file_name"]
            public_lb = submission_row["public_lb"]
        else:
            submission_file = ""
            public_lb = ""

        improvement_vs_phase2 = round(float(tracker_row["cv_macro_f1"]) - float(phase2["cv_macro_f1"]), 6)
        rows.append(
            {
                "rank": spec["rank"],
                "role": spec["role"],
                "status": spec["status"],
                "run_id": spec["run_id"],
                "submission_id": spec["submission_id"],
                "candidate_name": spec["candidate_name"],
                "feature_set": tracker_row["feature_set"],
                "model": tracker_row["model"],
                "cv_macro_f1": round(float(tracker_row["cv_macro_f1"]), 6),
                "cv_std": round(float(tracker_row["cv_std"]), 6),
                "oof_macro_f1": spec["oof_macro_f1"],
                "improvement_vs_phase2": improvement_vs_phase2,
                "submission_file": submission_file,
                "public_lb": public_lb,
                "reason_to_keep": spec["reason_to_keep"],
                "main_strength": spec["main_strength"],
                "main_risk": spec["main_risk"],
            }
        )

    return pd.DataFrame(rows).sort_values("rank")


def render_final_comparison_sheet(
    branch_config: dict,
    candidate_df: pd.DataFrame,
) -> str:
    """Render the final showdown sheet for M1."""
    phase2 = branch_config["phase_2_result"]
    phase3 = branch_config["phase_3_result"]
    phase4 = branch_config["phase_4_result"]
    phase5 = branch_config["phase_5_result"]

    progress_rows = [
        ["Phase 2", "exp_m1_001", "text baseline", f"{phase2['cv_macro_f1']:.6f}", f"{phase2['cv_std']:.6f}", "first clean end-to-end pipeline"],
        ["Phase 3", phase3["best_run_id"], phase3["best_direction"], f"{phase3['cv_macro_f1']:.6f}", f"{phase3['cv_std']:.6f}", "binary word representation beats standard TF-IDF"],
        ["Phase 4", phase4["best_run_id"], phase4["best_direction"], f"{phase4['cv_macro_f1']:.6f}", f"{phase4['cv_std']:.6f}", "text-only ensemble becomes branch winner"],
        ["Phase 5", phase4["best_run_id"], "error-analysis validation", f"{phase5['ensemble_oof_macro_f1']:.6f}", "-", "ensemble remains justified after case-level inspection"],
    ]

    candidate_rows = []
    for _, row in candidate_df.iterrows():
        oof_value = "" if row["oof_macro_f1"] == "" else f"{float(row['oof_macro_f1']):.6f}"
        submission_value = row["submission_file"] if row["submission_file"] else "not_submitted_yet"
        candidate_rows.append(
            [
                str(int(row["rank"])),
                row["role"],
                row["run_id"],
                row["model"],
                f"{float(row['cv_macro_f1']):.6f}",
                f"{float(row['cv_std']):.6f}",
                oof_value,
                submission_value,
                row["status"],
            ]
        )

    main_row = candidate_df.iloc[0]
    backup_row = candidate_df.iloc[1]
    stability_row = candidate_df.iloc[2]

    return f"""# Final Comparison Sheet - M1

## Branch snapshot

- Owner: `{branch_config['branch']['owner']}`
- Branch: `{branch_config['branch']['name']}`
- Current branch theme: `{branch_config['showdown_ready']['branch_strength']}`
- Current comparison status: `{branch_config['showdown_ready']['comparison_status']}`

## Executive decision

- **Main candidate to send into branch showdown:** `{main_row['run_id']}` (`{main_row['candidate_name']}`)
- **Primary backup:** `{backup_row['run_id']}` (`{backup_row['candidate_name']}`)
- **Stability reserve:** `{stability_row['run_id']}` (`{stability_row['candidate_name']}`)

## Why M1 is competitive

- M1 found a clean progression from baseline -> tuned single model -> text-only ensemble, instead of jumping into unnecessary hybrid complexity.
- The current winner `exp_m1_014` is not only the best CV candidate of M1, but also more stable than the best single model.
- Error analysis shows the ensemble improves the branch in a real way, especially on Label 1 and Label 4, not just by random fold noise.

## Progress timeline

{markdown_table(["Stage", "Run ID", "Direction", "CV Macro F1", "Std", "Key takeaway"], progress_rows)}

## Candidate board for showdown

{markdown_table(["Rank", "Role", "Run ID", "Model", "CV Macro F1", "Std", "OOF Macro F1", "Submission", "Status"], candidate_rows)}

## Main candidate profile

- Run ID: `{main_row['run_id']}`
- Submission file: `{main_row['submission_file']}`
- CV Macro F1: `{float(main_row['cv_macro_f1']):.6f}`
- CV std: `{float(main_row['cv_std']):.6f}`
- Reason to keep: {main_row['reason_to_keep']}
- Main strength: {main_row['main_strength']}
- Main risk: {main_row['main_risk']}

## Backup candidate profile

- Run ID: `{backup_row['run_id']}`
- Submission file: `{backup_row['submission_file']}`
- CV Macro F1: `{float(backup_row['cv_macro_f1']):.6f}`
- CV std: `{float(backup_row['cv_std']):.6f}`
- Reason to keep: {backup_row['reason_to_keep']}
- Main strength: {backup_row['main_strength']}
- Main risk: {backup_row['main_risk']}

## Stability reserve profile

- Run ID: `{stability_row['run_id']}`
- CV Macro F1: `{float(stability_row['cv_macro_f1']):.6f}`
- CV std: `{float(stability_row['cv_std']):.6f}`
- Reason to keep: {stability_row['reason_to_keep']}
- Main strength: {stability_row['main_strength']}
- Main risk: {stability_row['main_risk']}

## Evidence from error analysis

- Ensemble OOF Macro F1: `{phase5['ensemble_oof_macro_f1']:.6f}`
- Single-model OOF Macro F1: `{phase5['single_oof_macro_f1']:.6f}`
- Fixed by ensemble: `{phase5['fixed_by_ensemble']}`
- Hurt by ensemble: `{phase5['hurt_by_ensemble']}`
- Hardest labels still left: `{", ".join(str(label) for label in phase5['hardest_labels'])}`
- Biggest gains:
  - Label 1 F1 delta: `{phase5['key_improvements']['label_1_f1_delta']:+.6f}`
  - Label 4 F1 delta: `{phase5['key_improvements']['label_4_f1_delta']:+.6f}`
- Main trade-off:
  - Label 5 F1 delta: `{phase5['main_tradeoff']['label_5_f1_delta']:+.6f}`

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
"""


def main() -> None:
    shared_config = load_config()
    branch_config = load_config(BRANCH_CONFIG_PATH)

    candidate_df = build_candidate_rows(shared_config, branch_config)

    candidates_csv_path = resolve_project_path(branch_config["outputs"]["final_comparison_candidates_csv"])
    sheet_path = resolve_project_path(branch_config["outputs"]["final_comparison_sheet"])

    candidates_csv_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_df.to_csv(candidates_csv_path, index=False)
    write_text_file(sheet_path, render_final_comparison_sheet(branch_config, candidate_df))

    print(f"Main candidate: {candidate_df.iloc[0]['run_id']}")
    print(f"Backup candidate: {candidate_df.iloc[1]['run_id']}")
    print(f"Comparison sheet saved to: {sheet_path}")


if __name__ == "__main__":
    main()
