#!/bin/bash -l
#$ -P lejlab2
#$ -j y
#$ -l h_rt=02:00:00
#$ -pe omp 4
#$ -l mem_per_core=8G

module load freesurfer/7.4.1
module load fsl/6.0.7.8

echo "=== Job started: $(date) ==="
echo "Config: $1"

conda run -n freesurfer python "$2" --config "$1"

echo "=== Job finished: $(date) ==="
