# Membranes

Autovalidate can optionally include two intracranial membranes in the label map: the **falx cerebri** and the **tentorium cerebelli**.

## What they are

- **Falx cerebri** — a rigid fold of dura mater that runs along the midline, separating the left and right cerebral hemispheres
- **Tentorium cerebelli** — a fold of dura mater that separates the cerebellum from the occipital lobes of the cerebrum

Including these structures in the finite element mesh allows the simulation to model their mechanical effect on brain motion during impact.

## How it works in the pipeline

Pre-computed binary masks for both structures are expected in the subject directory:

```
*_register_to_tMRI/
    *_tMRIreg_falx.nii.gz
    *_tMRIreg_tentorium.nii.gz
```

At runtime:
1. Both masks are resampled to match the T1 image space using `mri_convert`
2. They are combined into a single membranes mask
3. Membrane voxels take priority over all other tissues during overlap resolution
4. The combined mask is assigned label `5`

## Label

| Label | Tissue |
|-------|--------|
| 5 | Membranes (falx + tentorium combined) |

## Config

```toml
[run]
include_membranes = true   # true / false
```

```toml
[env]
mri_convert = "/path/to/freesurfer/bin/mri_convert"  # required when include_membranes = true
```

> **Note:** The falx and tentorium masks in the NITRC dataset are pre-segmented and registered to the T1 space. If you are using a different dataset, you will need to provide these masks yourself. See [Bring Your Own Subject Data](tutorials/own_data.md) for details.
