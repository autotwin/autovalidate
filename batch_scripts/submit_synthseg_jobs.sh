#!/bin/bash
for file in /projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Original_T1_Scans/*.nii.gz; do
  base=$(basename "$file" .nii.gz)
  qsub run_synthseg.qsub "$file" "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/SynthSeg_result_files/${base}_SynthSeg.nii.gz"
done