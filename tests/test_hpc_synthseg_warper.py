import os
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import the main function from the script
from scripts.hpc_synthseg_warper import main

def test_run_single_scan_args(monkeypatch):
    """
    Test that run_single_scan.py correctly parses command line arguments
    and passes them to the run_synthseg_and_resample_strain function.
    """
    # 1. Define dummy paths we pretend were typed in the terminal
    fake_t1 = "/dummy/Original_T1_Scans/U01_HJF_0001_01_tMRIreg_T1.nii.gz"
    fake_strain_root = "/dummy/Original_Strain_Scans"
    fake_synthseg_out = "/dummy/SynthSeg_Outputs"
    fake_resamp_out = "/dummy/Resampled_Strain_Scans"
    fake_mri_synthseg = "/opt/freesurfer/bin/mri_synthseg"
    fake_mri_convert = "/opt/freesurfer/bin/mri_convert"

    # 2. Simulate the sys.argv as if the user ran it from bash
    test_args = [
        "scripts/hpc_synthseg_warper.py", # sys.argv[0] is always the script name
        "--t1", fake_t1,
        "--strain-root", fake_strain_root,
        "--synthseg-out", fake_synthseg_out,
        "--resamp-out", fake_resamp_out,
        "--mri-synthseg", fake_mri_synthseg,
        "--mri-convert", fake_mri_convert
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    # 3. Create a dictionary to catch the arguments passed to the pipeline
    captured_kwargs = {}

    def mock_run_synthseg_and_resample_strain(**kwargs):
        captured_kwargs.update(kwargs)

    # 4. Intercept the function call inside the script using monkeypatch
    monkeypatch.setattr(
        "scripts.hpc_synthseg_warper.run_synthseg_and_resample_strain", 
        mock_run_synthseg_and_resample_strain
    )

    # 5. Run the script's main function
    main()

    # 6. Assert that argparse correctly converted strings to Paths and passed them
    assert captured_kwargs["t1_root"] == Path(fake_t1)
    assert captured_kwargs["strain_root"] == Path(fake_strain_root)
    assert captured_kwargs["synthseg_root"] == Path(fake_synthseg_out)
    assert captured_kwargs["resampled_strain_root"] == Path(fake_resamp_out)
    assert captured_kwargs["mri_synthseg_path"] == Path(fake_mri_synthseg)
    assert captured_kwargs["mri_convert_path"] == Path(fake_mri_convert)
    assert captured_kwargs["extra_args"] == []
