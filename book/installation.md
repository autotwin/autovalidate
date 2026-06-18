# Installation

## Requirements

- Python 3.11 or higher
- At least one external segmentation tool, depending on the algorithm you choose (see below)

## Install the package

Clone the repository and install in editable mode:

```bash
git clone https://github.com/autotwin/autovalidate.git
cd autovalidate
pip install -e .
```

This installs the `autovalidate` package along with its Python dependencies:
`nibabel`, `numpy`, `scipy`, `scikit-image`.

## Verify the installation

```bash
python -c "import autovalidate; print('OK')"
```

Run the test suite to confirm everything works:

```bash
python -m pytest tests/ -v
```

## External tools

Each segmentation algorithm requires specific tools installed separately. Only install what you need.

### SynthSeg

SynthSeg is part of [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/). Install FreeSurfer 7.4 or higher, then locate the following binaries:

```
/path/to/freesurfer/bin/mri_synthseg
/path/to/freesurfer/bin/mri_convert
```

Both paths go in the `[env]` section of your config file. `mri_convert` is also required whenever `include_membranes = true`, regardless of algorithm.

### FSL FAST

[FSL](https://fsl.fmrib.ox.ac.uk) provides `bet` (brain extraction) and `fast` (tissue segmentation). After installing FSL, locate:

```
/path/to/fsl/bin/bet
/path/to/fsl/bin/fast
```

### SLANT

SLANT (MA-CRUISE) segmentations are pre-computed — no additional tool is required at runtime. The pipeline reads the existing `*_tMRIreg_macruise.nii.gz` file directly from the subject directory. `mri_convert` is only needed if `include_membranes = true`.
