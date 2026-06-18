# Introduction

Autovalidate is a brain mask generation pipeline that converts a subject's T1 MRI into a unified, simulation-ready label map.

## What it does

Given a T1 image, Autovalidate:

1. Runs a segmentation algorithm to identify brain tissues
2. Builds a skull layer around the brain via morphological dilation
3. Optionally includes falx cerebri and tentorium cerebelli membranes
4. Resolves any overlapping labels between tissues
5. Combines everything into a single integer label map saved as `.npy` and `.nii.gz`

## What it produces

For each subject, Autovalidate saves two files under `{output_dir}/{algorithm}/{fidelity}/{membranes}/{subject_id}/`:

- **`combined.npy`** — integer label array, used directly by automesh for mesh generation
- **`combined_labels.nii.gz`** — the same label map in NIfTI format, for visual inspection in tools like ITK-SNAP or FSLeyes

The label values follow a fixed schema (see [Volume Labels](labels.md)).

The resulting label map is passed directly to [automesh](https://github.com/autotwin/automesh) for mesh generation and then to [autosim](https://github.com/autotwin/autosim) for finite element simulation.

## Where it fits

```
T1 MRI
  └── autovalidate  →  combined label map (.npy)
        └── automesh     →  finite element mesh (.inp)
              └── autosim      →  simulation results (.odb)
```

## Supported algorithms

Autovalidate supports three segmentation algorithms — [SynthSeg](algorithms/synthseg.md), [FSL FAST](algorithms/fsl.md), and [SLANT](algorithms/slant.md) — and two fidelity levels: [homogeneous](fidelity.md) and [heterogeneous](fidelity.md).
