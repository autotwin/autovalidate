# FSL FAST

FSL FAST (FMRIB's Automated Segmentation Tool) segments a brain-extracted T1 image into three tissue classes: CSF, grey matter, and white matter.

## How it works in the pipeline

1. **BET** (`bet`) skull-strips the T1 image to produce a brain mask
2. **FAST** (`fast`) segments the brain-extracted image into 3 tissue classes
3. The output is mapped to the [common label schema](../labels.md)

## Label mapping

FAST produces a hard segmentation with integer labels:

| FAST label | Autovalidate label |
|------------|--------------------|
| 0 (background) | 0 (background) |
| 1 (CSF) | 3 (CSF) |
| 2 (GM) | 2 (GM) in heterogeneous; 1 (Brain) in homogeneous |
| 3 (WM) | 1 (WM) in heterogeneous; 1 (Brain) in homogeneous |

## Required tools

```toml
[env]
bet          = "/path/to/fsl/bin/bet"
fast         = "/path/to/fsl/bin/fast"
mri_convert  = "/path/to/freesurfer/bin/mri_convert"  # only if include_membranes = true
```

## Config

```toml
[run]
algorithm = "fsl"
```
