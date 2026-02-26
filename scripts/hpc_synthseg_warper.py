#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from autovalidate.pipeline import run_synthseg_and_resample_strain

def main():
    parser = argparse.ArgumentParser(description="Process a single T1 scan.")
    parser.add_argument("--t1", required=True, type=Path)
    parser.add_argument("--strain-root", required=True, type=Path)
    parser.add_argument("--synthseg-out", required=True, type=Path)
    parser.add_argument("--resamp-out", required=True, type=Path)
    parser.add_argument("--mri-synthseg", required=True, type=Path)
    parser.add_argument("--mri-convert", required=True, type=Path)
    args = parser.parse_args()

    run_synthseg_and_resample_strain(
        t1_root=args.t1, 
        strain_root=args.strain_root,
        synthseg_root=args.synthseg_out,
        resampled_strain_root=args.resamp_out,
        mri_synthseg_path=args.mri_synthseg,
        mri_convert_path=args.mri_convert,
        extra_args=[],
    )

if __name__ == "__main__":
    main()
