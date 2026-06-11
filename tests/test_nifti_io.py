import numpy as np
import nibabel as nib
import pytest

from autovalidate.io.nifti_io import load_nifti, save_nifti

def test_load_nifti(tmp_path):

    file_path = tmp_path / "test.nii.gz"

    input_array = np.zeros((3,3,3), dtype = np.uint8)
    input_array[0,0,0] = 1
    input_array[1,2,2] = 1
    input_array[2,1,2] = 1
    input_array[2,2,2] = 1

    affine_array = np.eye(4)

    dummy_file = nib.Nifti1Image(input_array,affine_array)

    nib.save(dummy_file,file_path)

    returned_array, returned_affine = load_nifti(file_path)

    np.testing.assert_array_equal(returned_array, input_array)
    np.testing.assert_array_equal(returned_affine, affine_array)


def test_load_nifti_no_nifti_file(tmp_path):

    file_path = tmp_path / "test.nii.gz"
    file_path.touch()

    with pytest.raises(ValueError):
        returned_array, returned_affine = load_nifti(file_path)
    

def test_save_nifti(tmp_path):

    file_path = tmp_path / "test.nii.gz"
    
    input_array = np.zeros((3,3,3), dtype = np.uint8)
    input_array[0,0,0] = 1
    input_array[1,2,2] = 1
    input_array[2,1,2] = 1
    input_array[2,2,2] = 1

    affine_array = np.eye(4)

    save_nifti(input_array, affine_array, file_path)

    img = nib.load(file_path)
    img_data = img.get_fdata()

    np.testing.assert_array_equal(img_data, input_array)
    np.testing.assert_array_equal(img.affine, affine_array)