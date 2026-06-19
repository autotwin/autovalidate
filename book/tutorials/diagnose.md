# Diagnose a Failed Segmentation

This tutorial covers the most common failure modes and how to fix them.

## 1. Subject directory or required file not found

**Error:**
```
FileNotFoundError: register_to_tMRI subdirectory not found in: /path/to/subject
```
or
```
FileNotFoundError: T1 file not found in: /path/to/subject/register_to_tMRI
```

**Cause:** The pipeline expects each subject directory to contain exactly one subdirectory ending in `register_to_tMRI`, with files named `*_tMRIreg_T1.nii.gz`, `*_tMRIreg_macruise.nii.gz`, etc. Any mismatch in directory name or file suffix will trigger this error.

**Fix:** Check the subject directory structure matches the expected layout:
```
{subject_dir}/
└── {prefix}_register_to_tMRI/
    ├── {prefix}_tMRIreg_T1.nii.gz
    ├── {prefix}_tMRIreg_macruise.nii.gz   # SLANT only
    ├── {prefix}_tMRIreg_falx.nii.gz        # membranes only
    └── {prefix}_tMRIreg_tentorium.nii.gz   # membranes only
```

See [Bring Your Own Subject Data](own_data.md) for the full file requirements per algorithm.

---

## 2. Tool binary not found

**Error:**
```
FileNotFoundError: mri_synthseg binary not found at '/path/to/mri_synthseg' — check your [env] config
```

**Cause:** The path specified in the `[env]` section of `config.toml` does not point to an existing executable.

**Fix:** Verify the path is correct and the tool is installed:
```bash
ls /path/to/freesurfer/bin/mri_synthseg
ls /path/to/fsl/bin/bet
```

Update the `[env]` section in your `config.toml` with the correct paths.

---

## 3. Invalid config value

**Error:**
```
ValueError: Wrong Segmentation Algorithm! Please select SynthSeg, FSL or SLANT
```
or
```
ValueError: Wrong Fidelity Level! Please select either Homogeneous or Heterogeneous
```
or
```
ValueError: Wrong motion type! Please select NR or NE
```

**Cause:** A field in the `[run]` section has an unexpected value. Field values are case-insensitive but must match exactly.

**Fix:** Check the allowed values:

| Field | Allowed values |
|-------|----------------|
| `algorithm` | `synthseg`, `fsl`, `slant` |
| `brain_fidelity` | `homogeneous`, `heterogeneous` |
| `motion_type` | `NR`, `NE` |
| `include_membranes` | `true`, `false` |

---

## 4. Missing required tool for the chosen algorithm

**Error:**
```
ValueError: mri_synthseg path not specified!
ValueError: bet path not specified!
```

**Cause:** The `[env]` section is missing a tool path required by the chosen algorithm.

**Fix:** Each algorithm requires specific tools in `[env]`:

| Algorithm | Required `[env]` keys |
|-----------|----------------------|
| `synthseg` | `mri_synthseg`, `mri_convert` |
| `fsl` | `bet`, `fast` |
| `slant` | *(none, unless membranes enabled)* |

If `include_membranes = true`, `mri_convert` is also required regardless of algorithm.

---

## 5. Empty or near-empty output label map

**Symptom:** The pipeline completes without errors but the output `.npy` file contains almost no labelled voxels, or a single tissue region dominates unexpectedly.

**Cause (FSL):** BET skull-stripping failed — the fractional intensity threshold (`-f 0.3`) may be too aggressive or too lenient for the subject, producing an empty or over-cropped brain mask. FAST then receives a bad input and produces a poor segmentation.

**Fix:** Enable `keep_intermediate_files = true` in `config.toml` and inspect the `intermediate/` directory:

```bash
ls {output_dir}/{algorithm}/{fidelity}/{membranes}/{subject_id}/intermediate/
```

Check `brain.nii.gz` (BET output) in ITK-SNAP. If the brain is missing or severely clipped, adjust BET's fractional intensity threshold in `autovalidate/segmentation/fsl.py`:

```python
def create_bet_command(..., fractional_intensity: float = 0.3):
```

Lower values (e.g. `0.2`) are more lenient; higher values (e.g. `0.5`) remove more non-brain tissue.

---

## 6. Membrane resampling fails

**Error:**
```
FileNotFoundError: Falx file not found in: /path/to/register_to_tMRI
```
or a subprocess error from `mri_convert`.

**Cause:** Either the falx/tentorium files are missing from the subject directory, or `mri_convert` is not correctly specified in `[env]`.

**Fix:**
- Confirm `*_tMRIreg_falx.nii.gz` and `*_tMRIreg_tentorium.nii.gz` exist in the `*register_to_tMRI` subdirectory.
- Confirm `mri_convert` is set correctly in `[env]` — it is required whenever `include_membranes = true`.
- If membranes are not needed for your use case, set `include_membranes = false` to skip this step entirely.
