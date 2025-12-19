cat > README.md << 'EOF'

# autovalidate

`autovalidate` is a Python workflow that turns T1‑weighted brain MRI and 4D strain data into
analysis‑ready **segmentations** and **labelmaps**. It wraps FreeSurfer's mri_convert and 
mri_synthseg with a set of Python utilities to:
- run **SynthSeg** on T1 scans,
- resample 4D **strain** fields to the SynthSeg grid (using the 2nd time frame),
- extract consistent **brain**, **CSF**, and **skull** masks, and
- combine them into a single labeled **head volume** (0=background, 1=brain, 2=CSF, 3=skull),
  along with NumPy arrays for downstream analysis.

The code is designed for use on local machines that have FreeSurfer installed, but remains
simple enough to run on an HPC cluster.

EOF