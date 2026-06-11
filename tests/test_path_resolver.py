from pathlib import Path
import pytest

from autovalidate.io.path_resolver import path_resolving

def test_path_resolving(tmp_path):

    tagged_sub_dir = tmp_path / "dummy_register_to_tMRI"
    tagged_sub_dir.mkdir()

    file_path1 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_T1.nii.gz"
    file_path1.touch()
    file_path2 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_macruise.nii.gz"
    file_path2.touch()
    file_path3 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_falx.nii.gz"
    file_path3.touch()
    file_path4 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_tentorium.nii.gz"
    file_path4.touch()

    algorithm = "slant"
    include_membranes = True

    path_dict = path_resolving(tmp_path, algorithm, include_membranes)

    assert path_dict["t1"] == file_path1
    assert path_dict["slant_seg"] == file_path2
    assert path_dict["falx"] == file_path3
    assert path_dict["tentorium"] == file_path4


def test_path_resolving_synthseg(tmp_path):

    tagged_sub_dir = tmp_path / "dummy_register_to_tMRI"
    tagged_sub_dir.mkdir()

    file_path1 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_T1.nii.gz"
    file_path1.touch()
    file_path2 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_macruise.nii.gz"
    file_path2.touch()
    file_path3 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_falx.nii.gz"
    file_path3.touch()
    file_path4 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_tentorium.nii.gz"
    file_path4.touch()

    algorithm = "synthseg"
    include_membranes = True

    path_dict = path_resolving(tmp_path, algorithm, include_membranes)

    assert path_dict["t1"] == file_path1
    assert path_dict["slant_seg"] == None
    assert path_dict["falx"] == file_path3
    assert path_dict["tentorium"] == file_path4


def test_path_resolving_no_membranes(tmp_path):

    tagged_sub_dir = tmp_path / "dummy_register_to_tMRI"
    tagged_sub_dir.mkdir()

    file_path1 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_T1.nii.gz"
    file_path1.touch()
    file_path2 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_macruise.nii.gz"
    file_path2.touch()
    file_path3 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_falx.nii.gz"
    file_path3.touch()
    file_path4 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_tentorium.nii.gz"
    file_path4.touch()

    algorithm = "synthseg"
    include_membranes = False

    path_dict = path_resolving(tmp_path, algorithm, include_membranes)

    assert path_dict["t1"] == file_path1
    assert path_dict["slant_seg"] == None
    assert path_dict["falx"] == None
    assert path_dict["tentorium"] == None

def test_path_resolving_no_directory(tmp_path):

    tagged_sub_dir = tmp_path / "dummy_register_to_tMRI"

    algorithm = "synthseg"
    include_membranes = False

    with pytest.raises(FileNotFoundError):
        path_dict = path_resolving(tmp_path, algorithm, include_membranes)


def test_path_resolving_no_T1(tmp_path):

    tagged_sub_dir = tmp_path / "dummy_register_to_tMRI"
    tagged_sub_dir.mkdir()

    file_path1 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_T1.nii.gz"
    file_path2 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_macruise.nii.gz"
    file_path2.touch()
    file_path3 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_falx.nii.gz"
    file_path3.touch()
    file_path4 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_tentorium.nii.gz"
    file_path4.touch()

    algorithm = "synthseg"
    include_membranes = False

    with pytest.raises(FileNotFoundError):
        path_dict = path_resolving(tmp_path, algorithm, include_membranes)


def test_path_resolving_no_macruise(tmp_path):

    tagged_sub_dir = tmp_path / "dummy_register_to_tMRI"
    tagged_sub_dir.mkdir()

    file_path1 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_T1.nii.gz"
    file_path1.touch()
    file_path2 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_macruise.nii.gz"
    file_path3 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_falx.nii.gz"
    file_path3.touch()
    file_path4 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_tentorium.nii.gz"
    file_path4.touch()

    algorithm = "slant"
    include_membranes = True

    with pytest.raises(FileNotFoundError):
        path_dict = path_resolving(tmp_path, algorithm, include_membranes)


def test_path_resolving_no_falx_file(tmp_path):

    tagged_sub_dir = tmp_path / "dummy_register_to_tMRI"
    tagged_sub_dir.mkdir()

    file_path1 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_T1.nii.gz"
    file_path1.touch()
    file_path2 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_macruise.nii.gz"
    file_path2.touch()
    file_path3 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_falx.nii.gz"
    file_path4 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_tentorium.nii.gz"
    file_path4.touch()

    algorithm = "synthseg"
    include_membranes = True

    with pytest.raises(FileNotFoundError):
        path_dict = path_resolving(tmp_path, algorithm, include_membranes)

def test_path_resolving_no_tentorium_file(tmp_path):

    tagged_sub_dir = tmp_path / "dummy_register_to_tMRI"
    tagged_sub_dir.mkdir()

    file_path1 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_T1.nii.gz"
    file_path1.touch()
    file_path2 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_macruise.nii.gz"
    file_path2.touch()
    file_path3 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_falx.nii.gz"
    file_path3.touch()
    file_path4 = tagged_sub_dir / "U01_HJF_0001_01_tMRIreg_tentorium.nii.gz"

    algorithm = "synthseg"
    include_membranes = True

    with pytest.raises(FileNotFoundError):
        path_dict = path_resolving(tmp_path, algorithm, include_membranes)


# ── SAMSEG-specific path tests ─────────────────────────────────────────────────



