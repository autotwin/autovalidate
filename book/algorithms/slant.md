# SLANT

SLANT (Spatially Localized Atlas Network Tiles) uses the MA-CRUISE algorithm to produce a detailed parcellation of the brain into 133 anatomical regions following the BrainCOLOR protocol.

Unlike SynthSeg and FSL, SLANT segmentations are **pre-computed** — the pipeline does not run any segmentation tool. It reads the existing `*_tMRIreg_macruise.nii.gz` file directly from the subject directory.

## How it works in the pipeline

1. The pre-computed segmentation file (`*_tMRIreg_macruise.nii.gz`) is loaded directly
2. The 133 BrainCOLOR labels are mapped to the [common label schema](../labels.md)
3. The rest of the pipeline (skull, membranes, overlap resolution) runs as normal

## Label mapping

SLANT uses 133 BrainCOLOR labels which are grouped as follows:

| SLANT labels | Autovalidate label |
|--------------|--------------------|
| 40, 41, 44, 45 | 1 (WM) in heterogeneous; 1 (Brain) in homogeneous |
| 23, 30–32, 35–39, 47–48, 55–60, 71–73, 75–76, 100–207 | 2 (GM) in heterogeneous; 1 (Brain) in homogeneous |
| 4, 11, 49–52 | 3 (CSF) |

## Required tools

No segmentation tool is required. `mri_convert` is only needed when `include_membranes = true`:

```toml
[env]
mri_convert = "/path/to/freesurfer/bin/mri_convert"  # only if include_membranes = true
```

## Config

```toml
[run]
algorithm = "slant"
```
