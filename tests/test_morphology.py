import os
from pathlib import Path

import nibabel as nib
import numpy as np
import pytest

from autovalidate.morphology import process_one_subject


def _save_mask(path: Path, data: np.ndarray, affine=None):
    if affine is None:
        affine = np.eye(4)
    img = nib.Nifti1Image(data.astype(np.uint8), affine)
    nib.save(img, str(path))


def test_process_one_subject_moves_interface_voxels(tmp_path):
    # Directory structure
    brain_dir = tmp_path / "brains"
    csf_dir = tmp_path / "csf"
    skull_dir = tmp_path / "skull"
    out_dir = tmp_path / "out"
    for d in (brain_dir, csf_dir, skull_dir, out_dir):
        d.mkdir()

    subject_root = "SUBJ_TEST"

    shape = (5, 5, 5)

    # Brain: a solid cube in the center
    brain = np.zeros(shape, dtype=bool)
    brain[2, 2, 2] = True

    # CSF: empty initially
    csf = np.zeros(shape, dtype=bool)

    # Skull: a one-voxel-thick shell around the center voxel
    skull = np.zeros(shape, dtype=bool)
    skull[1:4, 2, 2] = True
    skull[2, 1:4, 2] = True
    skull[2, 2, 1:4] = True

    # Save input masks
    _save_mask(brain_dir / f"{subject_root}_brain_mask.nii.gz", brain)
    _save_mask(csf_dir / f"{subject_root}_CSF_mask.nii.gz", csf)
    _save_mask(skull_dir / f"{subject_root}_braincsf_outer_shell.nii.gz", skull)

    # Run
    process_one_subject(
        BRAIN_DIR=str(brain_dir),
        CSF_DIR=str(csf_dir),
        SKULL_DIR=str(skull_dir),
        OUT_DIR=str(out_dir),
        subject_root=subject_root,
    )

    skull_out = out_dir / f"{subject_root}_skull_without_interface.nii.gz"
    csf_out = out_dir / f"{subject_root}_CSF_with_interface.nii.gz"

    assert skull_out.exists()
    assert csf_out.exists()

    skull_new = nib.load(str(skull_out)).get_fdata().astype(bool)
    csf_new = nib.load(str(csf_out)).get_fdata().astype(bool)

    # Shapes preserved
    assert skull_new.shape == shape
    assert csf_new.shape == shape

    # No overlap between new skull and CSF
    assert np.count_nonzero(skull_new & csf_new) == 0

    # Interface voxels should have been moved from skull to CSF:
    # original skull had nonzero voxels
    assert np.count_nonzero(skull) > np.count_nonzero(skull_new)
    assert np.count_nonzero(csf_new) > np.count_nonzero(csf)


def test_process_one_subject_missing_inputs(tmp_path, capsys):
    brain_dir = tmp_path / "brains"
    csf_dir = tmp_path / "csf"
    skull_dir = tmp_path / "skull"
    out_dir = tmp_path / "out"
    for d in (brain_dir, csf_dir, skull_dir, out_dir):
        d.mkdir()

    subject_root = "SUBJ_MISSING"

    # Only create brain, leave csf + skull missing
    _save_mask(brain_dir / f"{subject_root}_brain_mask.nii.gz", np.zeros((3, 3, 3)))

    process_one_subject(
        BRAIN_DIR=str(brain_dir),
        CSF_DIR=str(csf_dir),
        SKULL_DIR=str(skull_dir),
        OUT_DIR=str(out_dir),
        subject_root=subject_root,
    )

    captured = capsys.readouterr()
    assert "Missing CSF:" in captured.out or "Missing skull:" in captured.out
    # No outputs should be created
    assert not any(out_dir.iterdir())
