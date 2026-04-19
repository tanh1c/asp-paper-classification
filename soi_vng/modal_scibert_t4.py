from __future__ import annotations

from pathlib import Path

import modal


app = modal.App("asp-paper-scibert-t4")
ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECT_REMOTE_DIR = "/root/asp-paper-classification"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "pandas>=2.0",
        "numpy>=1.24",
        "scikit-learn>=1.3",
        "torch",
        "transformers",
    )
    .add_local_file(
        ROOT_DIR / "soi_vng/scibert_classifier_experiment.py",
        remote_path=f"{PROJECT_REMOTE_DIR}/soi_vng/scibert_classifier_experiment.py",
    )
    .add_local_file(
        ROOT_DIR / "soi_vng/structured_text_embedding_experiment.py",
        remote_path=f"{PROJECT_REMOTE_DIR}/soi_vng/structured_text_embedding_experiment.py",
    )
    .add_local_file(
        ROOT_DIR / "soi_vng/ensemble_experiment.py",
        remote_path=f"{PROJECT_REMOTE_DIR}/soi_vng/ensemble_experiment.py",
    )
    .add_local_dir(
        ROOT_DIR / "dataset_stage1",
        remote_path=f"{PROJECT_REMOTE_DIR}/dataset_stage1",
    )
)

outputs = modal.Volume.from_name("asp-paper-scibert-outputs", create_if_missing=True)


@app.function(
    image=image,
    gpu="T4",
    memory=8192,
    timeout=60 * 60 * 3,
    volumes={"/outputs": outputs},
)
def run_scibert_on_t4(
    folds: int = 5,
    epochs: int = 4,
    full_epochs: int = 4,
    batch_size: int = 8,
    max_length: int = 160,
    learning_rate: float = 2e-5,
    weight_decay: float = 0.01,
) -> list[str]:
    import shutil
    import subprocess
    from pathlib import Path

    project_dir = Path("/root/asp-paper-classification")
    work_output = project_dir / "soi_vng" / "scibert_outputs"
    volume_output = Path("/outputs")

    command = [
        "python",
        "soi_vng/scibert_classifier_experiment.py",
        "--folds",
        str(folds),
        "--epochs",
        str(epochs),
        "--full-epochs",
        str(full_epochs),
        "--batch-size",
        str(batch_size),
        "--max-length",
        str(max_length),
        "--learning-rate",
        str(learning_rate),
        "--weight-decay",
        str(weight_decay),
    ]

    subprocess.run(command, cwd=project_dir, check=True)

    volume_output.mkdir(parents=True, exist_ok=True)
    for path in work_output.glob("*"):
        if path.is_file():
            shutil.copy2(path, volume_output / path.name)
    outputs.commit()

    return sorted(path.name for path in volume_output.glob("*"))


@app.local_entrypoint()
def main(
    folds: int = 5,
    epochs: int = 4,
    full_epochs: int = 4,
    batch_size: int = 8,
    max_length: int = 160,
    learning_rate: float = 2e-5,
    weight_decay: float = 0.01,
):
    files = run_scibert_on_t4.remote(
        folds=folds,
        epochs=epochs,
        full_epochs=full_epochs,
        batch_size=batch_size,
        max_length=max_length,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
    )
    print("Files written to Modal volume `asp-paper-scibert-outputs`:")
    for file in files:
        print(f"- {file}")
