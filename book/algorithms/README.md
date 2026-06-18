# Algorithms

Autovalidate supports three segmentation algorithms. Each produces the same output format — a unified label map with a fixed schema — but differs in how brain tissues are identified.

| Algorithm | Input | Required tools | Notes |
|-----------|-------|----------------|-------|
| [SynthSeg](synthseg.md) | T1 image | `mri_synthseg`, `mri_convert` | Runs at pipeline time |
| [FSL FAST](fsl.md) | T1 image | `bet`, `fast` | Runs at pipeline time |
| [SLANT](slant.md) | Pre-computed segmentation | `mri_convert` (membranes only) | Reads existing file |

> **Dataset note:** This pipeline was originally built for the [NITRC](https://www.nitrc.org/) dataset, which provides pre-computed MA-CRUISE segmentations for each subject. This is why SLANT does not run any tool at pipeline time — the segmentation file is already there. SynthSeg and FSL run at pipeline time and work with any T1 image.

The algorithm is set in the config file:

```toml
[run]
algorithm = "synthseg"  # synthseg / fsl / slant
```
