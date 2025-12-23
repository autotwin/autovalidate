# tests/test_cleanup.py

import os
from pathlib import Path

import nibabel as nib
import numpy as np

from autovalidate.cleanup import fix_overlaps_for_subject


def _save_mask(path: Path, data: np.ndarray):
    img = nib.Nifti1Image(data.astype(np.uint8), np.eye(4))
    nib.save(img, str(path))


def test_fix_overlaps_for_subject(tmp_path):
    # Directory structure
    brain_dir = tmp_path / "brains"
    csf_dir = tmp_path / "csf"
    skull_dir = tmp_path / "skull"
    out_dir = tmp_path / "out"
    for d in (brain_dir, csf_dir, skull_dir, out_dir):
        d.mkdir()

    subj_root = "U01_HJF_0001_01"

    shape = (4, 4, 4)

    # Start with disjoint masks
    brain = np.zeros(shape, dtype=bool)
    csf = np.zeros(shape, dtype=bool)
    skull = np.zeros(shape, dtype=bool)

    brain[1, 1, 1] = True
    csf[1, 2, 1] = True
    skull[2, 2, 1] = True

    # Introduce overlaps:
    # voxel [1,1,1] in all three
    csf[1, 1, 1] = True
    skull[1, 1, 1] = True
    # voxel [1,2,1] in CSF & skull
    skull[1, 2, 1] = True

    # Save inputs with expected names
    brain_file = brain_dir / f"{subj_root}_tMRIreg_T1_SynthSeg_brain_mask.nii.gz"
    csf_file = csf_dir / f"{subj_root}_tMRIreg_T1_SynthSeg_CSF_with_interface.nii.gz"
    skull_file = skull_dir / f"{subj_root}_tMRIreg_T1_SynthSeg_skull_without_interface.nii.gz"

    _save_mask(brain_file, brain)
    _save_mask(csf_file, csf)
    _save_mask(skull_file, skull)

    # Run cleanup
    fix_overlaps_for_subject(
        BRAIN_DIR=str(brain_dir),
        CSF_DIR=str(csf_dir),
        SKULL_DIR=str(skull_dir),
        OUT_DIR=str(out_dir),
        subj_root=subj_root,
    )

    brain_out = out_dir / f"{subj_root}_brain_clean.nii.gz"
    csf_out = out_dir / f"{subj_root}_csf_clean.nii.gz"
    skull_out = out_dir / f"{subj_root}_skull_clean.nii.gz"

    # Outputs exist
    assert brain_out.exists()
    assert csf_out.exists()
    assert skull_out.exists()

    brain_clean = nib.load(str(brain_out)).get_fdata().astype(bool)
    csf_clean = nib.load(str(csf_out)).get_fdata().astype(bool)
    skull_clean = nib.load(str(skull_out)).get_fdata().astype(bool)

    # No overlaps remain, respecting hierarchy brain > CSF > skull
    assert np.count_nonzero(brain_clean & csf_clean) == 0
    assert np.count_nonzero(brain_clean & skull_clean) == 0
    assert np.count_nonzero(csf_clean & skull_clean) == 0

    # Priority checks at specific voxels:
    # [1,1,1] was in all three; brain should win.
    assert bool(brain_clean[1, 1, 1]) is True
    assert bool(csf_clean[1, 1, 1]) is False
    assert bool(skull_clean[1, 1, 1]) is False

    # [1,2,1] was in CSF & skull; CSF should win.
    assert bool(csf_clean[1, 2, 1]) is True
    assert bool(skull_clean[1, 2, 1]) is False

    # Original disjoint voxels preserved
    assert bool(skull_clean[2, 2, 1]) is True
