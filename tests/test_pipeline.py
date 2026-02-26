import os
import sys
from pathlib import Path
import subprocess
import pytest
import numpy as np
import nibabel as nib

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from autovalidate.pipeline import find_t1_scans, run_synthseg_and_resample_strain

def test_run_synthseg_and_resample_strain(tmp_path, monkeypatch):
    # Setup test directories
    t1_root = tmp_path / "Original_T1_Scans"
    strain_root = tmp_path / "Original_Strain_Scans"
    synthseg_root = tmp_path / "SynthSeg_Outputs"
    resamp_root = tmp_path / "Resampled_Strain_Scans"
    
    t1_root.mkdir()
    strain_root.mkdir()

    # Create dummy T1 file
    f1 = t1_root / "U01_HJF_0001_01_tMRIreg_T1.nii.gz"
    f1.write_text("x")

    # Create a real 4D dummy strain NIfTI file (e.g., 2x2x2 space with 3 time frames)
    f_strain = strain_root / "U01_HJF_0001_01_NR_HFE12_r5_E1_fit.nii.gz"
    dummy_4d_data = np.zeros((2, 2, 2, 3), dtype=np.float32)
    dummy_img = nib.Nifti1Image(dummy_4d_data, np.eye(4))
    nib.save(dummy_img, str(f_strain))

    # Test file discovery
    scans = find_t1_scans(t1_root)
    assert scans == [f1]

    # Mock executables
    synthseg_exe = Path("/opt/SynthSeg/mri_synthseg")
    convert_exe = Path("/opt/SynthSeg/mri_convert")

    calls: list[list[str]] = []

    def fake_run(cmd, stdout=None, stderr=None, text=None):
        # record command
        calls.append(cmd)
        # pretend success
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    # Intercept subprocess.run
    monkeypatch.setattr(subprocess, "run", fake_run)

    # Call the pipeline
    run_synthseg_and_resample_strain(
        t1_root=t1_root,
        strain_root=strain_root,
        synthseg_root=synthseg_root,
        resampled_strain_root=resamp_root,
        mri_synthseg_path=synthseg_exe,
        mri_convert_path=convert_exe,
        extra_args=["--threads", "4"],
    )

    # We expect 1 SynthSeg call + 3 mri_convert calls (because we made a dummy 4D file with 3 frames)
    assert len(calls) == 4

    seg_cmd = calls[0]
    conv_cmd1 = calls[1]

    # Verify SynthSeg command
    assert seg_cmd[0] == str(synthseg_exe)
    assert "--i" in seg_cmd and "--o" in seg_cmd
    assert str(f1) in seg_cmd
    expected_seg_out = synthseg_root / "U01_HJF_0001_01_tMRIreg_T1_SynthSeg.nii.gz"
    assert str(expected_seg_out) in seg_cmd
    assert "--threads" in seg_cmd and "4" in seg_cmd

    # Verify First mri_convert command
    assert conv_cmd1[0] == str(convert_exe)
    assert conv_cmd1[1:3] == ["--resample_type", "interpolate"]
    
    # Check that it uses a temporary frame file as input
    tmp_input = conv_cmd1[3]
    assert tmp_input.endswith("strain_frame0_tmp.nii.gz")
    
    # Check the --like target
    assert conv_cmd1[4] == "--like"
    assert conv_cmd1[5] == str(expected_seg_out)
    
    # Check output resampled frame target
    final_output = conv_cmd1[6]
    assert final_output.endswith("_frame0_strain_resamp.nii.gz")
    assert "U01_HJF_0001_01" in final_output
