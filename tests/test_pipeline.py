import os
import sys
from pathlib import Path

import subprocess
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from autovalidate.pipeline import find_t1_scans, run_synthseg_and_resample_t1


def test_build_synthseg_commands(tmp_path, monkeypatch):
    src = tmp_path / "Original_T1_Scans"
    src.mkdir()
    f1 = src / "U01_subj1_tMRIreg_T1.nii.gz"
    f2 = src / "U01_subj2_tMRIreg_T1.nii.gz"
    f3 = src / "notes.txt"
    for f in (f1, f2, f3):
        f.write_text("x")

    scans = find_t1_scans(src)
    assert scans == [f1, f2]

    out_root = tmp_path / "SynthSeg"
    synthseg_exe = Path("/opt/SynthSeg/synthseg_predict")  # placeholder
    convert_command = Path("/opt/SynthSeg/mri_convert")

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

    monkeypatch.setattr(subprocess, "run", fake_run)

    run_synthseg_and_resample_t1(
        input_root=src,
        synthseg_root=out_root,
        resampled_t1_root=tmp_path / "Resampled_T1_Scans",
        mri_synthseg_path=synthseg_exe,
        mri_convert_path=convert_command,
    )

    # For 2 inputs, expect 4 subprocess calls: 2 x mri_synthseg + 2 x mri_convert
    assert len(calls) == 4

    seg_cmd1 = calls[0]
    conv_cmd1 = calls[1]

    # First SynthSeg command
    assert seg_cmd1[0] == str(synthseg_exe)
    assert "--i" in seg_cmd1 and "--o" in seg_cmd1
    assert str(f1) in seg_cmd1
    expected_seg_out = out_root / "U01_subj1_tMRIreg_T1_SynthSeg.nii.gz"
    assert str(expected_seg_out) in seg_cmd1

    # First mri_convert command: mri_convert --resample_type nearest in --like out out_resamp
    assert conv_cmd1[0] == str(convert_command)
    assert conv_cmd1[1:3] == ["--resample_type", "nearest"]
    assert str(f1) == conv_cmd1[3]          # input_label
    assert conv_cmd1[4] == "--like"
    assert conv_cmd1[5] == str(expected_seg_out)
    assert conv_cmd1[6].endswith("_resamp.nii.gz")
