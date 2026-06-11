import pytest
from pathlib import Path

from autovalidate.io.file_io import collect_files_by_keyword, copy_files, create_mri_convert_command, create_ants_apply_transforms_command


def test_collect_files_by_keyword(tmp_path):

    tagged_sub_dir = tmp_path / "tagged"
    tagged_sub_dir.mkdir()
    slant_sub_dir = tmp_path / "slant"
    slant_sub_dir.mkdir()
    
    T1_keyword = ["tMRI_T1"]
    falx_keyword = ["falx"]

    file_path1 = tagged_sub_dir / "tMRI_T1.nii.gz"
    file_path1.touch()
    file_path2 = tagged_sub_dir / "wrong_filename.nii.gz"
    file_path2.touch()
    file_path3 = slant_sub_dir / "falx.nii.gz"
    file_path3.touch()
    file_path4 = slant_sub_dir / "T2.nii.gz"
    file_path4.touch()

    T1_image = collect_files_by_keyword(tagged_sub_dir, T1_keyword)
    falx_image = collect_files_by_keyword(slant_sub_dir, falx_keyword)

    assert T1_image == [file_path1]
    assert falx_image == [file_path3]

def test_collect_files_by_keyword_FileNotFoundError_case(tmp_path):

    non_existent_dir = tmp_path / "tagged"
    
    T1_keyword = ["tMRI_T1"]

    with pytest.raises(FileNotFoundError):
        T1_image = collect_files_by_keyword(non_existent_dir, T1_keyword)

def test_collect_files_by_keyword_NotADirectoryError_case(tmp_path):

    tmp_dir = tmp_path / "tagged"
    tmp_dir.mkdir()
    
    falx_keyword = ["falx"]

    file_path1 = tmp_dir / "falx.nii.gz"
    file_path1.touch()
    
    with pytest.raises(NotADirectoryError):
        falx_image = collect_files_by_keyword(file_path1, falx_keyword)  

def test_collect_files_by_keyword_EmptyDirectory_case(tmp_path):

    tmp_dir = tmp_path / "tagged"
    tmp_dir.mkdir()
    
    falx_keyword = ["falx"]

    falx_image = collect_files_by_keyword(tmp_dir, falx_keyword)

    assert falx_image == []

def test_collect_files_by_keyword_NoKeywordMatch_case(tmp_path):
    
    tmp_dir = tmp_path / "tagged"
    tmp_dir.mkdir()
    
    falx_keyword = ["falx"]

    file_path1 = tmp_dir / "tMRI_T1.nii.gz"
    file_path1.touch()

    falx_image = collect_files_by_keyword(tmp_dir, falx_keyword)

    assert falx_image == []

def test_collect_files_by_keyword_extension(tmp_path):
    
    tagged_sub_dir = tmp_path / "tagged"
    tagged_sub_dir.mkdir()
    slant_sub_dir = tmp_path / "slant"
    slant_sub_dir.mkdir()
    
    T1_keyword = ["tMRI_T1"]
    falx_keyword = ["falx"]

    file_path1 = tagged_sub_dir / "tMRI_T1.nii.gz"
    file_path1.touch()
    file_path3 = slant_sub_dir / "falx.mat"
    file_path3.touch()


    T1_image = collect_files_by_keyword(tagged_sub_dir, T1_keyword, extension=".nii.gz")
    falx_image = collect_files_by_keyword(slant_sub_dir, falx_keyword, extension=".mat")

    assert T1_image == [file_path1]
    assert falx_image == [file_path3]

def test_collect_files_by_keyword_wrong_extension(tmp_path):
    
    slant_sub_dir = tmp_path / "slant"
    slant_sub_dir.mkdir()

    falx_keyword = ["falx"]

    file_path3 = slant_sub_dir / "falx.nii.gz"
    file_path3.touch()

    falx_image = collect_files_by_keyword(slant_sub_dir, falx_keyword, extension=".mat")

    assert falx_image == []

def test_copy_files(tmp_path):

    dummy_path1 = tmp_path / "dummy1.nii.gz"
    dummy_path1.touch()
    dummy_path2 = tmp_path / "dummy2.nii.gz"
    dummy_path2.touch() 
    list_of_paths = [dummy_path1,dummy_path2]

    target_dir = tmp_path / "target_directory"
    target_dir.mkdir()

    copy_files(list_of_paths, target_dir)

    moved_dummy1 = Path(f"{target_dir}/{dummy_path1.name}")
    moved_dummy2 = Path(f"{target_dir}/{dummy_path2.name}")

    assert moved_dummy1.exists()
    assert moved_dummy2.exists()

def test_copy_files_create_dir(tmp_path):

    dummy_path1 = tmp_path / "dummy1.nii.gz"
    dummy_path1.touch()
    dummy_path2 = tmp_path / "dummy2.nii.gz"
    dummy_path2.touch() 
    list_of_paths = [dummy_path1,dummy_path2]

    target_dir = tmp_path / "target_directory"

    copy_files(list_of_paths, target_dir)

    moved_dummy1 = Path(f"{target_dir}/{dummy_path1.name}")
    moved_dummy2 = Path(f"{target_dir}/{dummy_path2.name}")

    assert moved_dummy1.exists()
    assert moved_dummy2.exists()

def test_create_mri_convert_command_no_additional_flags():

    mri_convert_path = Path("dummy/path/to/mri_convert")
    input_file = Path("dummy/path/to/input/file")
    output_file = Path("dummy/path/to/output/file")

    lines = create_mri_convert_command(mri_convert_path, input_file, output_file)

    assert len(lines) == 3
    assert lines[0] == str(mri_convert_path)
    assert lines[1] == str(input_file)
    assert lines[2] == str(output_file)

def test_create_mri_convert_command_with_additional_flags():

    mri_convert_path = Path("dummy/path/to/mri_convert")
    input_file = Path("dummy/path/to/input/file")
    output_file = Path("dummy/path/to/output/file")
    like_file = Path("dummy/path/to/like_file")

    lines = create_mri_convert_command(mri_convert_path, input_file, output_file, like_path = like_file, resample_type = "nearest")

    assert len(lines) == 7
    assert lines[0] == str(mri_convert_path)
    assert lines[2] == "nearest"
    assert lines[5] == str(like_file)

def test_create_mri_convert_command_ValueError_no_likepath():

    mri_convert_path = Path("dummy/path/to/mri_convert")
    input_file = Path("dummy/path/to/input/file")
    output_file = Path("dummy/path/to/output/file")

    with pytest.raises(ValueError):
        lines = create_mri_convert_command(mri_convert_path, input_file, output_file, resample_type = "nearest")

def test_create_mri_convert_command_ValueError_no_resampletype():

    mri_convert_path = Path("dummy/path/to/mri_convert")
    input_file = Path("dummy/path/to/input/file")
    output_file = Path("dummy/path/to/output/file")
    like_file = Path("dummy/path/to/like_file")

    with pytest.raises(ValueError):
        lines = create_mri_convert_command(mri_convert_path, input_file, output_file, like_path=like_file)

def test_create_ants_apply_transforms_command():

    ants_path = Path("dummy/path/to/ants")
    input_file = Path("dummy/path/to/input/file")
    reference_file = Path("dummy/to/reference/file")
    transformation_file = Path("dummy/to/transformation/matrix")
    output_file = Path("dummy/path/to/output/file")

    lines = create_ants_apply_transforms_command(ants_path, input_file, reference_file, transformation_file, output_file)

    assert len(lines) == 13
    assert lines[0] == str(ants_path)
    assert lines[4] == str(input_file)
    assert lines[8] == str(transformation_file)
