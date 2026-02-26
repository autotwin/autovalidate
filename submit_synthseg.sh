#!/bin/bash -l
#$ -P lejlab2                 
#$ -N synthseg_array          
#$ -j y                       
#$ -l h_rt=04:00:00           
#$ -pe omp 4                  

# ===================== USER CONFIGURATION =====================
BASE_DIR="path/to/study"

T1_ROOT="$BASE_DIR/Original_T1_Scans"
STRAIN_ROOT="$BASE_DIR/Original_Strain_Scans"
SYNTHSEG_OUT="$BASE_DIR/SynthSeg_Outputs"
RESAMP_OUT="$BASE_DIR/Resampled_Strain_Scans"

MRI_SYNTHSEG_PATH="/share/pkg.8/freesurfer/7.4.1_CentOS-8/install/freesurfer/bin/mri_synthseg"
MRI_CONVERT_PATH="/share/pkg.8/freesurfer/7.4.1_CentOS-8/install/freesurfer/bin/mri_convert"
# =================== END USER CONFIGURATION ===================

module load freesurfer/7.4.1

# 1. Search the root directory and securely load all matching files into a sorted array
mapfile -t FILES < <(find "$T1_ROOT" -maxdepth 1 -name "*T1*.nii.gz" | sort)
NUM_FILES=${#FILES[@]}

if [ "$NUM_FILES" -eq 0 ]; then
    echo "Error: No T1 scans found in $T1_ROOT"
    exit 1
fi

# 2. If run manually in terminal, print the qsub command and exit
if [ -z "$SGE_TASK_ID" ] || [ "$SGE_TASK_ID" == "undefined" ]; then
    echo "Found $NUM_FILES T1 scans in $T1_ROOT."
    echo "To run one job per file, submit this script by running:"
    echo "qsub -t 1-$NUM_FILES submit_synthseg.sh"
    exit 0
fi

# 3. If running as a cluster job, grab ONLY the file assigned to this task ID
INDEX=$((SGE_TASK_ID - 1))
CURRENT_T1=${FILES[$INDEX]}

echo "Task ID: $SGE_TASK_ID | Processing exactly one file: $(basename "$CURRENT_T1")"

# 4. Pass this single file to the Python wrapper
python3 scripts/run_single_scan.py \
    --t1 "$CURRENT_T1" \
    --strain-root "$STRAIN_ROOT" \
    --synthseg-out "$SYNTHSEG_OUT" \
    --resamp-out "$RESAMP_OUT" \
    --mri-synthseg "$MRI_SYNTHSEG_PATH" \
    --mri-convert "$MRI_CONVERT_PATH"
