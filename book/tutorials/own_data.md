# Bring Your Own Subject Data

This tutorial explains how to prepare your own subject data so that Autovalidate can process it.

## Required directory structure

Autovalidate expects each subject to have a specific directory layout. The subject directory must contain one subdirectory whose name ends in `register_to_tMRI`, and all required files must live inside it:

```
{subject_dir}/
└── {any_prefix}_register_to_tMRI/
    ├── {prefix}_tMRIreg_T1.nii.gz          # T1 image (always required)
    ├── {prefix}_tMRIreg_macruise.nii.gz    # SLANT pre-computed segmentation
    ├── {prefix}_tMRIreg_falx.nii.gz        # falx membrane mask
    └── {prefix}_tMRIreg_tentorium.nii.gz   # tentorium membrane mask
```

The prefix can be anything — the pipeline uses glob patterns to find the files. Only the suffix after `_tMRIreg_` matters.

## Which files are required

| File | Required when |
|------|---------------|
| `*_tMRIreg_T1.nii.gz` | Always |
| `*_tMRIreg_macruise.nii.gz` | `algorithm = "slant"` |
| `*_tMRIreg_falx.nii.gz` | `include_membranes = true` |
| `*_tMRIreg_tentorium.nii.gz` | `include_membranes = true` |

For `synthseg` and `fsl`, only the T1 image is needed (plus the membrane files if membranes are enabled).

## Setting up `config.toml`

Copy the template from the repo root and fill in the subject-specific fields:

```toml
[env]
mri_convert  = "/path/to/freesurfer/bin/mri_convert"
mri_synthseg = "/path/to/freesurfer/bin/mri_synthseg"

[run]
algorithm             = "synthseg"
brain_fidelity        = "homogeneous"
include_membranes     = true
motion_type           = "NR"
subject_dir           = "/path/to/my_subject"
output_dir            = "/path/to/results"
subject_id            = "my_subject"
keep_intermediate_files = false
```

### `motion_type`

`motion_type` tags the output filename and is used to locate experimental data for comparison. Set it to:

- `NR` — Neck Rotation
- `NE` — Neck Extension

If you are not comparing against experimental data, either value works — it only affects the output filename.

### `subject_id`

`subject_id` is the name used for the output directory and output files. It does not need to match the directory name on disk.

## Running the pipeline

```bash
python run.py --config /path/to/my_subject.toml
```

Output files will appear under:

```
{output_dir}/{algorithm}/{brain_fidelity}/{membranes}/{subject_id}/
    {subject_id}-{motion_type}-{algorithm}-{brain_fidelity}-{membranes}-combined.npy
    {subject_id}-{motion_type}-{algorithm}-{brain_fidelity}-{membranes}-combined_labels.nii.gz
```

## Running on multiple subjects

Create one TOML file per subject in a directory and use the HPC submitter:

```bash
python hpc/submit.py --configs /path/to/configs/
```

The submitter skips any subject whose output already exists, so it is safe to re-run after a partial failure. See the [HPC chapter](../hpc.md) for cluster-specific setup.
