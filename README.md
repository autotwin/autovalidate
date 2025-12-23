# Autovalidate : Brain–CSF–Skull + Strain Processing Pipeline

`Autovalidate` is a Python workflow that turns T1‑weighted brain MRI and 4D strain data into
analysis‑ready **segmentations** and **labelmaps**. It wraps FreeSurfer's `mri_convert` and 
`mri_synthseg` with a set of Python utilities to:
- run **SynthSeg** on T1 scans,
- resample 4D **strain** fields to the SynthSeg grid (using the 2nd time frame),
- extract consistent **brain**, **CSF**, and **skull** masks, and
- combine them into a single labeled **head volume** (0=background, 1=brain, 2=CSF, 3=skull),
  along with NumPy arrays for downstream analysis.

The code is designed for use on local machines that have FreeSurfer installed, but remains
simple enough to run on an HPC cluster.


## Key points

- **Inputs**: T1‑weighted brain MRI volumes and 4D Lagrangian strain fields in NIfTI format.
- **Outputs**: Consistent brain, CSF, and skull masks, plus a single labeled head volume 
(0=background, 1=brain, 2=CSF, 3=skull) and NumPy arrays for downstream analysis.
- **Dependencies**: FreeSurfer (for `mri_convert` and `mri_synthseg`), Python 3.9 or later, 
and common scientific Python packages such as NumPy and NiBabel.
- **Execution**: Designed for local workstations with FreeSurfer installed, but the workflow
 can also be run on HPC clusters using batch scripts.
- **Use cases**: Voxel‑wise strain analysis, segmentation quality control, and generation of 
head masks for computational mechanics workflows.


## Getting Started

### Installation

1. Clone this repository from GitHub:
git clone https://github.com/autotwin/autovalidate.git
cd autovalidate

2. (Optional) Create and activate a Python environment, for example with `conda`:
conda create -n autovalidate python=3.9
conda activate autovalidate

3. Install Python dependencies:
pip install -r requirements.txt

4. Ensure FreeSurfer is installed and configured.

   This workflow assumes that FreeSurfer is installed and that the commands
   `mri_convert` and `mri_synthseg` are available in your shell.

   You can quickly check this with:

   **Option 1**: check the environment variable
   echo "$FREESURFER_HOME"

   **Option 2**: check the binaries are on your PATH
   which mri_convert
   which mri_synthseg

   If these commands return empty output or “not found”, FreeSurfer is not set
   up correctly. Please follow the official FreeSurfer installation and setup
   instructions for your platform:

   - Linux and macOS installation: https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall
   - Example Linux setup (FREESURFER_HOME and SetUpFreeSurfer scripts): https://surfer.nmr.mgh.harvard.edu/fswiki/LinuxInstall

### Usage

After installation and FreeSurfer setup, you can run the pipeline on a 
single or multiple subjects.

1. Edit `scripts/move_scans.py` to point to your input and output directories,
then run it to collect the scans.
2. Edit `scripts/run_synthseg_locally.py` to set your FreeSurfer/SynthSeg paths,
then run it to segment the T1 scans.
3. Edit `scripts/extract_components.py` to set paths, then run it to extract
brain, CSF, and skull components.
4. Edit `scripts/create_boundary_layer.py` to set paths, then run it to
build the CSF–skull boundary layer.
5. Edit `scripts/fix_overlaps.py` to set paths, then run it to clean up
mask overlaps.
6. Edit `scripts/combine_all.py` to set paths, then run it to combine masks 
nd strain fields into final outputs.

Running this sequence will generate:

- A labeled head volume with background (label = 0), brain (label =1),
CSF (label=2), and skull (label=3) labels.
- Separate brain/CSF/skull masks.
- NumPy arrays ready for downstream analysis or meshing.