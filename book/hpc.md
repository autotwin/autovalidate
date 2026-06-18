# HPC

Autovalidate includes two scripts in the `hpc/` directory for running the pipeline at scale on a cluster:

- **`hpc/submit.py`** — reads a directory of per-subject TOML configs and submits one job per subject
- **`hpc/job.sh`** — the job script executed on the compute node

These scripts were written for the **Boston University Shared Computing Cluster (SCC)** which uses the **SGE** scheduler. If your cluster uses a different scheduler (SLURM, PBS, LSF), you will need to adapt them — see [Adapting to your cluster](#adapting-to-your-cluster) below.

---

## How it works

### 1. Create per-subject config files

Create one TOML config file per subject in a directory (e.g. `hpc/configs/`). Each file follows the same format as described in [Configuration Reference](configuration.md).

The `hpc/configs/` directory is excluded from git by default (see `.gitignore`).

### 2. Submit all jobs

```bash
python hpc/submit.py --configs /path/to/configs/
```

For each config file, `submit.py`:
- Checks if the output `.npy` file already exists — **skips** the subject if so
- Creates the output directory for the subject
- Submits a job via `qsub`, writing logs to `{subject_output_dir}/job.log`

### 3. The job script

Each submitted job runs `hpc/job.sh`, which:
1. Loads the required modules (`freesurfer`, `fsl`)
2. Activates the conda environment
3. Calls `python run.py --config <config_file>`

---

## Skip logic

`submit.py` skips a subject if the output `.npy` file already exists at:

```
{output_dir}/{algorithm}/{fidelity}/{membranes}/{subject_id}/
    {subject_id}-{motion_type}-{algorithm}-{fidelity}-{membranes}-combined.npy
```

This means you can safely re-run `submit.py` at any time — completed subjects are automatically skipped and only missing ones are submitted.

---

## Adapting to your cluster

The parts that need changing for a different scheduler or environment are:

| What to change | SGE (current) | SLURM equivalent | PBS equivalent |
|----------------|---------------|------------------|----------------|
| Submit command | `qsub` | `sbatch` | `qsub` |
| Job directives | `#$ -l h_rt=...` | `#SBATCH --time=...` | `#PBS -l walltime=...` |
| Parallelism | `#$ -pe omp N` | `#SBATCH --cpus-per-task=N` | `#PBS -l ncpus=N` |
| Memory | `#$ -l mem_per_core=8G` | `#SBATCH --mem-per-cpu=8G` | `#PBS -l mem=32gb` |
| Array jobs | `#$ -t 1-N` | `#SBATCH --array=1-N` | `#PBS -J 1-N` |
| Module system | `module load freesurfer/7.4.1` | same (if modules available) | same |
| Conda activation | `conda run -n freesurfer python ...` | same | same |

In `submit.py`, replace the `qsub` call with the appropriate command for your scheduler. In `job.sh`, replace the `#$` directives with those of your scheduler and update the module names to match what your cluster provides.
