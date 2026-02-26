import os
import sys
from pathlib import Path

import nibabel as nib
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from autovalidate.segmentation import (
    extract_brain,
    extract_CSF,
    process_all_brain_csf_skulls,
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


def test_brain_csf_skull_pipeline(tmp_path):
    # 1) Setup synthetic directory structure
    synthseg_dir = tmp_path / "SynthSeg_Outputs"
    brain_dir = tmp_path / "Extracted_Brains"
    csf_dir = tmp_path / "Extracted_CSF"
    skull_dir = tmp_path / "Extracted_Skull"
    
    synthseg_dir.mkdir()

    # 2) Create a synthetic segmentation
    shape = (8, 8, 8)
    seg = np.zeros(shape, dtype=int)
    seg[2:6, 2:6, 2:6] = 42      # brain-ish block
    seg[3:5, 3:5, 3:5] = 24      # CSF-ish core

    seg_name = "U01_TEST_tMRIreg_T1_SynthSeg_resamp.nii.gz"
    seg_path = synthseg_dir / seg_name
    _make_seg_nii(seg_path, seg)

    # 3) Run the full extraction pipeline
    process_all_brain_csf_skulls(
        synthseg_root=synthseg_dir,
        brain_out=brain_dir,
        csf_out=csf_dir,
        skull_out=skull_dir,
        thickness_voxels=2,
        min_cc_size=1,
    )

    # 4) Verify outputs exist with the correct naming scheme
    brain_path = brain_dir / "U01_TEST_tMRIreg_T1_SynthSeg_resamp_brain_mask.nii.gz"
    csf_path = csf_dir / "U01_TEST_tMRIreg_T1_SynthSeg_resamp_CSF_mask.nii.gz"
    expected_skull_name = "U01_TEST_tMRIreg_T1_SynthSeg_resamp_skull_mask.nii.gz"
    skull_path = skull_dir / expected_skull_name
    
    assert brain_path.exists()
    assert csf_path.exists()
    assert skull_path.exists()

    # 5) Verify skull logic
    skull = nib.load(skull_path).get_fdata()
    assert skull.shape == shape
    assert skull.dtype in (np.float32, np.float64, np.uint8, np.int16)

    skull_mask = skull > 0
    assert np.count_nonzero(skull_mask) > 0

    brain_mask = nib.load(brain_path).get_fdata() > 0
    csf_mask = nib.load(csf_path).get_fdata() > 0
    brain_csf = brain_mask | csf_mask

    # No skull voxels strictly inside brain+CSF
    assert np.count_nonzero(skull_mask & brain_csf) == 0

