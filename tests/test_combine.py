# tests/test_combine.py

import os
import sys
from pathlib import Path

import nibabel as nib
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from autovalidate.combine import combine_all_components


def _save_mask(path: Path, data: np.ndarray):
    img = nib.Nifti1Image(data.astype(np.uint8), np.eye(4))
    nib.save(img, str(path))


def test_combine_all_components(tmp_path):
    # Directory structure
    brain_dir = tmp_path / "brains"
    csf_dir = tmp_path / "csf"
    skull_dir = tmp_path / "skull"
    strain_dir = tmp_path / "strains"
    out_dir = tmp_path / "out"
    
    for d in (brain_dir, csf_dir, skull_dir, strain_dir, out_dir):
        d.mkdir()

    subj_root = "U01_HJF_0001_01"
    shape = (4, 4, 4)

    # Define simple disjoint masks
    brain = np.zeros(shape, dtype=bool)
    csf = np.zeros(shape, dtype=bool)
    skull = np.zeros(shape, dtype=bool)

    brain[1, 1, 1] = True
    csf[1, 2, 1] = True
    skull[2, 2, 1] = True

    # 1. Save inputs matching the expected "_clean" naming from combine.py
    brain_file = brain_dir / f"{subj_root}_brain_clean.nii.gz"
    csf_file = csf_dir / f"{subj_root}_csf_clean.nii.gz"
    skull_file = skull_dir / f"{subj_root}_skull_clean.nii.gz"

    _save_mask(brain_file, brain)
    _save_mask(csf_file, csf)
    _save_mask(skull_file, skull)

    # 2. Create a dummy strain file to trigger the "NR" detection logic
    dummy_strain_file = strain_dir / f"{subj_root}_NR_HFE12_r5_E1_fit.nii.gz"
    dummy_strain_file.write_text("dummy")

    # Run combiner
    combine_all_components(
        BRAIN_DIR=str(brain_dir),
        CSF_DIR=str(csf_dir),
        SKULL_DIR=str(skull_dir),
        STRAIN_DIR=str(strain_dir),
        OUT_DIR=str(out_dir),
        subj_root=subj_root,
    )

    # 3. Check for the new filename format that includes _NR
    expected_nii_name = f"{subj_root}_NR_tMRIreg_T1_SynthSeg_combined_labels.nii.gz"
    expected_npy_name = f"{subj_root}_NR_tMRIreg_T1_SynthSeg_combined_labels.npy"
    
    out_nii_file = out_dir / expected_nii_name
    out_npy_file = out_dir / expected_npy_name
    
    assert out_nii_file.exists()
    assert out_npy_file.exists()

    labels = nib.load(str(out_nii_file)).get_fdata().astype(np.uint8)
    assert labels.shape == shape

    # Check label encoding: 0=bg, 1=brain, 2=CSF, 3=skull
    assert labels[1, 1, 1] == 1  # brain
    assert labels[1, 2, 1] == 2  # CSF
    assert labels[2, 2, 1] == 3  # skull
    assert labels[0, 0, 0] == 0  # background

