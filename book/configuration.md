# Configuration Reference

All pipeline settings are specified in a TOML file passed to `run.py`:

```bash
python run.py --config my_subject.toml
```

Use `config.toml` in the repo root as a starting template.

---

## `[env]` — Tool paths

Tool paths are only required for the tools actually used by the chosen algorithm.

| Field | Required for | Description |
|-------|-------------|-------------|
| `mri_synthseg` | SynthSeg | Path to the `mri_synthseg` binary |
| `mri_convert` | SynthSeg, membranes | Path to the `mri_convert` binary |
| `bet` | FSL | Path to the FSL `bet` binary |
| `fast` | FSL | Path to the FSL `fast` binary |

**Example:**
```toml
[env]
mri_synthseg = "/share/pkg.8/freesurfer/7.4.1/install/freesurfer/bin/mri_synthseg"
mri_convert  = "/share/pkg.8/freesurfer/7.4.1/install/freesurfer/bin/mri_convert"
```

---

## `[run]` — Pipeline settings

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `algorithm` | string | yes | Segmentation algorithm: `synthseg`, `fsl`, or `slant` |
| `brain_fidelity` | string | yes | Fidelity level: `homogeneous` or `heterogeneous` |
| `include_membranes` | bool | yes | Whether to include falx and tentorium membranes |
| `motion_type` | string | yes | Subject motion type: `NR` or `NE` |
| `subject_dir` | string | yes | Absolute path to the subject's data directory |
| `output_dir` | string | yes | Base output directory — results are saved under `output_dir/algorithm/fidelity/membranes/subject_id/` |
| `subject_id` | string | yes | Subject identifier (e.g. `U01_HJF_0001_01`) |
| `keep_intermediate_files` | bool | no | If `true`, intermediate files (e.g. BET brain mask, SynthSeg output) are kept in `subject_dir/intermediate/`. Default: `false` |

**Example:**
```toml
[run]
algorithm               = "synthseg"
brain_fidelity          = "homogeneous"
include_membranes       = true
motion_type             = "NR"
subject_dir             = "/path/to/U01_HJF_0001_01_v4"
output_dir              = "/path/to/results"
subject_id              = "U01_HJF_0001_01"
keep_intermediate_files = false
```

---

## Output path

The output files are saved at:

```
{output_dir}/{algorithm}/{fidelity}/{membranes}/{subject_id}/
    {subject_id}-{motion_type}-{algorithm}-{fidelity}-{membranes}-combined.npy
    {subject_id}-{motion_type}-{algorithm}-{fidelity}-{membranes}-combined_labels.nii.gz
```

For example:

```
results/synthseg/homogeneous/membranesON/U01_HJF_0001_01/
    U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy
    U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined_labels.nii.gz
```
