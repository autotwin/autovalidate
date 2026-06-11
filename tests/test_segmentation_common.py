import numpy as np

from autovalidate.segmentation.common import extract_mask

def test_extract_mask_include_mode():

    dummy_array = np.array([[[0, 24], [2, 0]],
                            [[2, 0], [24, 0]]])
    
    labels = [24]

    expected_array = np.array([[[0, 1], [0, 0]],
                               [[0, 0], [1, 0]]])

    mask = extract_mask(dummy_array, labels, exclude=False)

    np.testing.assert_array_equal(mask, expected_array)
    assert mask.dtype == np.uint8

def test_extract_mask_exclude_mode():

    dummy_array = np.array([[[0, 24], [2, 0]],
                            [[2, 0], [24, 0]]])
    
    labels = [24]

    expected_array = np.array([[[1, 0], [1, 1]],
                               [[1, 1], [0, 1]]])

    mask = extract_mask(dummy_array, labels, exclude=True)

    np.testing.assert_array_equal(mask, expected_array)
    assert mask.dtype == np.uint8


def test_extract_mask_empty_labels():

    dummy_array = np.array([[[0, 24], [2, 0]],
                            [[2, 0], [24, 0]]])
    
    labels = []

    expected_array_False = np.array([[[0, 0], [0, 0]],
                                     [[0, 0], [0, 0]]])

    expected_array_True = np.array([[[1, 1], [1, 1]],
                                    [[1, 1], [1, 1]]])

    mask_False = extract_mask(dummy_array, labels, exclude=False)

    mask_True = extract_mask(dummy_array, labels, exclude=True)

    np.testing.assert_array_equal(mask_False, expected_array_False)
    np.testing.assert_array_equal(mask_True, expected_array_True)
    assert mask_False.dtype == np.uint8
    assert mask_True.dtype == np.uint8