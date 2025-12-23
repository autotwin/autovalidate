import os
from pathlib import Path

import nibabel as nib
import numpy as np

from autovalidate.segmentation import (
    extract_brain,
    extract_CSF,
    process_all_brain_csf_shells,
)


def _make_seg_nii(path: Path, data: np.ndarray) -> None:
    img = nib.Nifti1Image(data.astype(np.int16), np.eye(4))
    nib.save(img, path)


def test_extract_brain_mask_logic_and_naming(tmp_path):
    seg = np.zeros((4, 4, 4), dtype=int)
    seg[1, 1, 1] = 42      # brain
    seg[2, 2, 2] = 24      # CSF

    in_name = "U01_TEST_tMRIreg_T1_SynthSeg_resamp.nii.gz"
    in_path = tmp_path / in_name
    _make_seg_nii(in_path, seg)

    dest = tmp_path / "brain_masks"
    extract_brain(str(in_path), str(dest))

    expected_name = "U01_TEST_tMRIreg_T1_SynthSeg_resamp_brain_mask.nii.gz"
    out_path = dest / expected_name
    assert out_path.exists()

    mask = nib.load(out_path).get_fdata()
    assert mask.shape == seg.shape
    assert mask[0, 0, 0] == 0       # background removed
    assert mask[2, 2, 2] == 0       # CSF (24) removed
    assert mask[1, 1, 1] == 1       # other label kept


def test_extract_CSF_mask_logic_and_naming(tmp_path):
    seg = np.zeros((4, 4, 4), dtype=int)
    seg[1, 1, 1] = 24      # CSF
    seg[2, 2, 2] = 42      # non‑CSF

    in_name = "U01_TEST_tMRIreg_T1_SynthSeg_resamp.nii.gz"
    in_path = tmp_path / in_name
    _make_seg_nii(in_path, seg)

    dest = tmp_path / "csf_masks"
    extract_CSF(str(in_path), str(dest))

    expected_name = "U01_TEST_tMRIreg_T1_SynthSeg_resamp_CSF_mask.nii.gz"
    out_path = dest / expected_name
    assert out_path.exists()

    mask = nib.load(out_path).get_fdata()
    assert mask.shape == seg.shape
    assert mask[1, 1, 1] == 1       # CSF kept
    assert mask[2, 2, 2] == 0       # non‑CSF removed
    assert mask[0, 0, 0] == 0       # background removed


def test_brain_csf_outer_shell_pipeline(tmp_path):
    # 1) Create a synthetic segmentation
    shape = (8, 8, 8)
    seg = np.zeros(shape, dtype=int)
    seg[2:6, 2:6, 2:6] = 42      # brain-ish block
    seg[3:5, 3:5, 3:5] = 24      # CSF-ish core

    seg_name = "U01_TEST_tMRIreg_T1_SynthSeg_resamp.nii.gz"
    seg_path = tmp_path / seg_name
    _make_seg_nii(seg_path, seg)

    # 2) Create brain and CSF masks using the real functions
    brain_dir = tmp_path / "brains"
    csf_dir = tmp_path / "csf"
    out_dir = tmp_path / "shells"
    brain_dir.mkdir()
    csf_dir.mkdir()
    out_dir.mkdir()

    extract_brain(str(seg_path), str(brain_dir))
    extract_CSF(str(seg_path), str(csf_dir))

    # 3) Run outer-shell creation over those masks
    process_all_brain_csf_shells(
        brain_dir=brain_dir,
        csf_dir=csf_dir,
        out_dir=out_dir,
        thickness_vox=2,
        min_cc_size=0,
    )

    expected_name = "U01_TEST_tMRIreg_T1_SynthSeg_resamp_braincsf_outer_shell.nii.gz"
    out_path = out_dir / expected_name
    assert out_path.exists()

    shell = nib.load(out_path).get_fdata()
    assert shell.shape == shape
    assert shell.dtype in (np.float32, np.float64, np.uint8, np.int16)

    # Work with boolean masks for logical operations
    shell_mask = shell > 0

    # Shell should be non-empty and outside the brain+CSF region
    assert np.count_nonzero(shell_mask) > 0

    brain_mask = nib.load(
        brain_dir / "U01_TEST_tMRIreg_T1_SynthSeg_resamp_brain_mask.nii.gz"
    ).get_fdata() > 0
    csf_mask = nib.load(
        csf_dir / "U01_TEST_tMRIreg_T1_SynthSeg_resamp_CSF_mask.nii.gz"
    ).get_fdata() > 0
    brain_csf = brain_mask | csf_mask

    # No shell voxels strictly inside brain+CSF
    assert np.count_nonzero(shell_mask & brain_csf) == 0
