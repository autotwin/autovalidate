import os
import sys
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from autovalidate.io import move_files_by_keyword


def test_move_files_by_keyword(tmp_path):
    source = tmp_path / "src"
    dest = tmp_path / "dst"
    source.mkdir()

    # Create dummy files
    f1 = source / "subj1_tMRIreg_T1.nii.gz"
    f2 = source / "subj2_r5_E1_fit.nii.gz"
    f3 = source / "notes.txt"
    for f in (f1, f2, f3):
        f.write_text("x")

    moved_orig = move_files_by_keyword(source, dest, ["T1.nii.gz"], confirm=False)
    moved_strain = move_files_by_keyword(source, dest, ["r5_E1_fit.nii.gz"], confirm=False)

    names = {p.name for p in (moved_orig + moved_strain)}
    assert names == {"subj1_tMRIreg_T1.nii.gz", "subj2_r5_E1_fit.nii.gz"}

    # Copies exist in destination
    assert (dest / "subj1_tMRIreg_T1.nii.gz").exists()
    assert (dest / "subj2_r5_E1_fit.nii.gz").exists()

    # Originals remain in source (copy, not move)
    assert (source / "subj1_tMRIreg_T1.nii.gz").exists()
    assert (source / "subj2_r5_E1_fit.nii.gz").exists()

    # Unrelated file is untouched
    assert (source / "notes.txt").exists()
    assert not (dest / "notes.txt").exists()