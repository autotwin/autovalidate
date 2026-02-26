import os
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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

    # Brain: solid cube
    brain = np.zeros(shape, dtype=bool)

    # CSF: A single voxel in the center
    csf = np.zeros(shape, dtype=bool)
    csf[2, 2, 2] = True

    # Skull: A cross shape surrounding the center CSF voxel
    skull = np.zeros(shape, dtype=bool)
    skull[1:4, 2, 2] = True
    skull[2, 1:4, 2] = True
    skull[2, 2, 1:4] = True
    skull[2, 2, 2] = False  # Keep the center clear so it doesn't overlap CSF initially

    # Save input masks
    _save_mask(brain_dir / f"{subject_root}_brain_mask.nii.gz", brain)
    _save_mask(csf_dir / f"{subject_root}_CSF_mask.nii.gz", csf)
    _save_mask(skull_dir / f"{subject_root}_skull_mask.nii.gz", skull)

    # Run
    process_one_subject(
        brain_dir=str(brain_dir),
        csf_dir=str(csf_dir),
        skull_dir=str(skull_dir),
        out_dir=str(out_dir),
        subject_root=subject_root,
        inner_thickness_voxels=1,
    )

    skull_out = out_dir / f"{subject_root}_skull_without_inner_layer.nii.gz"
    csf_out = out_dir / f"{subject_root}_CSF_with_inner_layer.nii.gz"

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
    # meaning the new skull has fewer voxels, and the new CSF has more.
    assert np.count_nonzero(skull) > np.count_nonzero(skull_new)
    assert np.count_nonzero(csf_new) > np.count_nonzero(csf)


def test_process_one_subject_missing_inputs(tmp_path):
    brain_dir = tmp_path / "brains"
    csf_dir = tmp_path / "csf"
    skull_dir = tmp_path / "skull"
    out_dir = tmp_path / "out"
    for d in (brain_dir, csf_dir, skull_dir, out_dir):
        d.mkdir()

    subject_root = "SUBJ_MISSING"

    # Only create brain, intentionally leave csf + skull missing
    _save_mask(brain_dir / f"{subject_root}_brain_mask.nii.gz", np.zeros((3, 3, 3)))

    # Instead of checking capsys print statements, we verify the code correctly
    # crashes by raising a FileNotFoundError when the masks don't exist.
    with pytest.raises(FileNotFoundError):
        process_one_subject(
            brain_dir=str(brain_dir),
            csf_dir=str(csf_dir),
            skull_dir=str(skull_dir),
            out_dir=str(out_dir),
            subject_root=subject_root,
            inner_thickness_voxels=1,
        )

    # Verify no outputs were created
    assert not any(out_dir.iterdir())
