#!/bin/bash

# Paths 
synthseg_input_dir="/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/SynthSeg_result_files"
# stats_parent="/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/IXI_Dataset/SynthSeg_Batch"  
mri_dir="/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Original_T1_Scans"
synthseg_resample_outdir="/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Resampled_segmented_files"
# freesurfer_resample_outdir="/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/IXI_Dataset/SynthSeg_Batch/Aseg_Resamp"

mkdir -p "$synthseg_resample_outdir"
# mkdir -p "$freesurfer_resample_outdir"

for scan in "$mri_dir"/*.nii.gz; do
    subj_synth=$(basename "${scan}" .nii.gz)
    synthseg="$synthseg_input_dir/${subj_synth}_SynthSeg.nii.gz"
    resamp_out="$synthseg_resample_outdir/${subj_synth}_SynthSeg_resamp.nii.gz"
    echo "Submitting resampling for $subj_synth"
    qsub run_resample.qsub "$synthseg" "$scan" "$resamp_out"
done

# for subj_dir in "$stats_parent"/*/; do
#   subj=$(basename "$subj_dir")
#   aseg_img="$subj_dir/stats/aseg.mgz"
#   orig="$orig_dir/${subj}.nii.gz"
#   outfile="$output_dir/${subj}_aseg_resamp.nii.gz"
#   if [[ -f "$aseg_img" && -f "$orig" ]]; then
#     echo "Submitting aseg resample for $subj"
#     qsub run_resample.qsub "$aseg_img" "$orig" "$outfile"
#   else
#     echo "Missing aseg or orig for $subj"
#   fi
# done