#!/usr/bin/env python3
import argparse
import tomllib
import subprocess
from pathlib import Path


def membranes_label(include_membranes: bool) -> str:
    return "membranesON" if include_membranes else "membranesOFF"


def subject_output_dir(cfg: dict) -> Path:
    run = cfg["run"]
    return (
        Path(run["output_dir"])
        / run["algorithm"].lower()
        / run["brain_fidelity"].lower()
        / membranes_label(run["include_membranes"])
        / run["subject_id"]
    )


def output_exists(cfg: dict) -> bool:
    run = cfg["run"]
    subject_dir = subject_output_dir(cfg)
    subject_id  = run["subject_id"]
    motion_type = run["motion_type"].upper()
    algorithm   = run["algorithm"].lower()
    fidelity    = run["brain_fidelity"].lower()
    membranes   = membranes_label(run["include_membranes"])
    filename    = f"{subject_id}-{motion_type}-{algorithm}-{fidelity}-{membranes}-combined.npy"
    return (subject_dir / filename).exists()


def main():
    parser = argparse.ArgumentParser(description="Submit one SGE job per config file.")
    parser.add_argument("--configs", required=True, type=Path,
                        help="Directory containing per-subject .toml config files")
    args = parser.parse_args()

    repo_root  = Path(__file__).resolve().parent.parent
    job_script = Path(__file__).resolve().parent / "job.sh"
    run_py     = repo_root / "run.py"

    config_files = sorted(args.configs.glob("*.toml"))
    print(f"Found {len(config_files)} config files\n")

    submitted = 0
    skipped   = 0

    for config_path in config_files:
        with open(config_path, "rb") as f:
            cfg = tomllib.load(f)

        subject_id = cfg["run"]["subject_id"]

        if output_exists(cfg):
            print(f"[skip]   {subject_id}  (output already exists)")
            skipped += 1
            continue

        log_dir = subject_output_dir(cfg)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "job.log"

        result = subprocess.run(
            [
                "qsub",
                "-o", str(log_file),
                "-N", subject_id,
                str(job_script),
                str(config_path),
                str(run_py),
            ],
            capture_output=True, text=True,
        )

        if result.returncode == 0:
            print(f"[submit] {subject_id}  {result.stdout.strip()}")
            submitted += 1
        else:
            print(f"[ERROR]  {subject_id}  {result.stderr.strip()}")

    print(f"\nDone. Submitted: {submitted}  Skipped: {skipped}")


if __name__ == "__main__":
    main()
