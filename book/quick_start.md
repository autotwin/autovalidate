# Quick Start

This guide walks through running the pipeline on a single subject using SynthSeg.

## 1. Create a config file

Copy the template from the repo root and fill in your paths:

```toml
[env]
mri_synthseg = "/path/to/freesurfer/bin/mri_synthseg"
mri_convert  = "/path/to/freesurfer/bin/mri_convert"

[run]
algorithm               = "synthseg"
brain_fidelity          = "homogeneous"
include_membranes       = true
motion_type             = "NR"
subject_dir             = "/path/to/subject_v4"
output_dir              = "/path/to/results"
subject_id              = "U01_HJF_0001_01"
keep_intermediate_files = false
```

Save it as `my_subject.toml`.

## 2. Run the pipeline

```bash
python run.py --config my_subject.toml
```

You should see:

```
[1/10] Loading config...
       subject=U01_HJF_0001_01  algorithm=synthseg  fidelity=homogeneous  membranes=True
[2/10] Validating tool paths...
       all tool paths OK
[3/10] Resolving input paths...
[4/10] Running segmentation (synthseg)...
[5/10] Extracting masks...
[6/10] Building skull...
[7/10] Resolving overlaps...
[8/10] Processing membranes...
[9/10] Combining labels (homogeneous)...
[10/10] Saving outputs...
        Saving .nii.gz...

Done. Output files:
  /path/to/results/synthseg/homogeneous/membranesON/U01_HJF_0001_01/U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy
  /path/to/results/synthseg/homogeneous/membranesON/U01_HJF_0001_01/U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined_labels.nii.gz
```

## 3. Check the output

The output directory will contain:

```
results/synthseg/homogeneous/membranesON/U01_HJF_0001_01/
    U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy
    U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined_labels.nii.gz
```

Load the `.nii.gz` in ITK-SNAP or FSLeyes to visually inspect the label map, or load the `.npy` in Python:

```python
import numpy as np
data = np.load("...combined.npy")
print(data.shape)       # e.g. (256, 256, 192)
print(np.unique(data))  # [0 1 3 4 5]
```

Label values: `0` = background, `1` = brain, `3` = CSF, `4` = skull, `5` = membranes. See [Volume Labels](labels.md) for the full schema.
