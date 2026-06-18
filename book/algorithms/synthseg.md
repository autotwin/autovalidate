# SynthSeg

SynthSeg v2 is a deep learning-based segmentation tool from [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/) that segments a T1 MRI into approximately 33 anatomical regions.

## How it works in the pipeline

1. `mri_synthseg` is called on the T1 image (`*_tMRIreg_T1.nii.gz`)
2. The output segmentation is mapped to the [common label schema](../labels.md)
3. The rest of the pipeline (skull, membranes, overlap resolution) runs as normal

## Label mapping

| SynthSeg labels | Autovalidate label |
|-----------------|--------------------|
| 2, 41 (WM) | 1 (WM) in heterogeneous; 1 (Brain) in homogeneous |
| 3, 42, 17, 18, 53, 54 ... (GM) | 2 (GM) in heterogeneous; 1 (Brain) in homogeneous |
| 4, 5, 14, 15, 24, 43, 44 ... (CSF/ventricles) | 3 (CSF) |

## Required tools

```toml
[env]
mri_synthseg = "/path/to/freesurfer/bin/mri_synthseg"
mri_convert  = "/path/to/freesurfer/bin/mri_convert"
```

`mri_convert` is required to resample the falx and tentorium masks when `include_membranes = true`.

## Config

```toml
[run]
algorithm = "synthseg"
```
