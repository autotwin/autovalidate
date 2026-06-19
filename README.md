# Autovalidate

Automated brain mask generation pipeline for finite element model validation.

Autovalidate takes a subject's T1 MRI and produces a unified label map (`.npy` + `.nii.gz`) ready for mesh generation and simulation. It supports three segmentation algorithms, two fidelity levels, and optional falx/tentorium membranes.

For detailed documentation on Autovalidate please check: [https://autotwin.github.io/autovalidate/](https://autotwin.github.io/autovalidate/)

## Installation

Python 3.11 or higher is required.

```bash
pip install -e .
```

Dependencies (`nibabel`, `numpy`, `scipy`, `scikit-image`) are installed automatically.

## Usage

```bash
python run.py --config config.toml
```

Copy `config.toml` from the repo root, fill in the paths, and run. See [Configuration](#configuration) for all fields.

## Algorithms

| Algorithm | Description | Required tools |
|-----------|-------------|----------------|
| `synthseg` | Runs SynthSeg v2 on the T1 image | `mri_synthseg`, `mri_convert` |
| `fsl` | BET skull-stripping followed by FAST tissue segmentation | `bet`, `fast` |
| `slant` | Reads a pre-computed MA-CRUISE segmentation (`*_tMRIreg_macruise.nii.gz`) | `mri_convert` (membranes only) |

## Output

Results are saved under:

```
{output_dir}/{algorithm}/{fidelity}/{membranes}/{subject_id}/
    {subject_id}-{motion_type}-{algorithm}-{fidelity}-{membranes}-combined.npy
    {subject_id}-{motion_type}-{algorithm}-{fidelity}-{membranes}-combined_labels.nii.gz
```

### Label schema

| Label | Homogeneous | Heterogeneous |
|-------|-------------|---------------|
| 0 | Background | Background |
| 1 | Brain | White Matter |
| 2 | — | Gray Matter |
| 3 | CSF | CSF |
| 4 | Skull | Skull |
| 5 | Membranes (if enabled) | Membranes (if enabled) |

## Configuration

All fields are set in a TOML file. Use `config.toml` in the repo root as a template.

```toml
[env]
mri_convert  = "/path/to/freesurfer/bin/mri_convert"   # required for SynthSeg + membranes
mri_synthseg = "/path/to/freesurfer/bin/mri_synthseg"  # required for SynthSeg
bet          = "/path/to/fsl/bin/bet"                   # required for FSL
fast         = "/path/to/fsl/bin/fast"                  # required for FSL

[run]
algorithm               = "synthseg"          # synthseg / fsl / slant
brain_fidelity          = "homogeneous"       # homogeneous / heterogeneous
include_membranes       = true                # include falx and tentorium
motion_type             = "NR"                # NR or NE
subject_dir             = "/path/to/subject"
output_dir              = "/path/to/results"
subject_id              = "U01_HJF_0001_01"
keep_intermediate_files = false               # keep BET/FAST/SynthSeg outputs
```

Only the tools required by the chosen algorithm need to be specified in `[env]`.

## HPC (SGE)

To submit one job per subject on a cluster, create a directory of per-subject TOML configs and run:

```bash
python hpc/submit.py --configs /path/to/configs/
```

The submitter skips subjects whose output already exists and writes logs to `{subject_dir}/job.log`.

## Development

Run the test suite:

```bash
python -m pytest tests/ -v
```
