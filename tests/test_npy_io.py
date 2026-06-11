import numpy as np
import pytest

from autovalidate.io.npy_io import save_npy

def test_save_npy(tmp_path):

    file_path = tmp_path / "test.npy"
    
    input_array = np.zeros((3,3,3), dtype = np.uint8)
    input_array[0,0,0] = 1
    input_array[1,2,2] = 1
    input_array[2,1,2] = 1
    input_array[2,2,2] = 1

    save_npy(input_array, file_path)

    array = np.load(file_path)

    np.testing.assert_array_equal(array, input_array)