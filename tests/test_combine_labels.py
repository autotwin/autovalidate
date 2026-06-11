import numpy as np
import pytest

from autovalidate.combine.combine_labels import combine_labels_homogeneous, combine_labels_heterogeneous


def test_combine_masks_homogeneous():

    brain = np.array([0, 1, 0, 0], dtype=np.uint8)
    CSF = np.array([0, 0, 1, 0], dtype=np.uint8)
    skull = np.array([0, 0, 0, 1], dtype=np.uint8)

    combined = combine_labels_homogeneous(brain,CSF,skull)

    np.testing.assert_array_equal(combined, np.array([0,1,3,4], dtype=np.uint8))


def test_combine_masks_homogeneous_with_membranes():

    brain = np.array([1, 0, 0, 0, 0], dtype=np.uint8)
    CSF = np.array([0, 1, 0, 0, 0], dtype=np.uint8)
    skull = np.array([0, 0, 1, 0, 0], dtype=np.uint8)
    membranes = np.array([0, 0, 0, 1, 0], dtype=np.uint8)

    combined = combine_labels_homogeneous(brain, CSF, skull, membranes)

    np.testing.assert_array_equal(combined, np.array([1, 3, 4, 5, 0], dtype=np.uint8))


def test_combine_masks_homogeneous_shape_mismatch():

    brain = np.array([1, 0, 0, 0], dtype=np.uint8)
    CSF = np.array([0, 1, 0, 0], dtype=np.uint8)
    skull = np.array([0, 0, 1], dtype=np.uint8)

    with pytest.raises(ValueError):
        combined = combine_labels_homogeneous(brain, CSF, skull)

def test_combine_masks_homogeneous_with_membranes_shape_mismatch():

    brain = np.array([1, 0, 0, 0, 0], dtype=np.uint8)
    CSF = np.array([0, 1, 0, 0, 0], dtype=np.uint8)
    skull = np.array([0, 0, 1, 0, 0], dtype=np.uint8)
    membranes = np.array([0, 0, 0, 1], dtype=np.uint8)

    with pytest.raises(ValueError):
        combined = combine_labels_homogeneous(brain, CSF, skull, membranes)


def test_combine_masks_heterogeneous():

    wm = np.array([0, 1, 0, 0, 0], dtype=np.uint8)
    gm = np.array([0, 0, 1, 0, 0], dtype=np.uint8)
    CSF = np.array([0, 0, 0, 1, 0], dtype=np.uint8)
    skull = np.array([0, 0, 0, 0, 1], dtype=np.uint8)

    combined = combine_labels_heterogeneous(wm, gm, CSF, skull)

    np.testing.assert_array_equal(combined, np.array([0,1,2,3,4], dtype=np.uint8))


def test_combine_masks_heterogeneous_with_membranes():

    wm = np.array([0, 1, 0, 0, 0, 0], dtype=np.uint8)
    gm = np.array([0, 0, 1, 0, 0, 0], dtype=np.uint8)
    CSF = np.array([0, 0, 0, 1, 0, 0], dtype=np.uint8)
    skull = np.array([0, 0, 0, 0, 1, 0], dtype=np.uint8)
    membranes = np.array([0, 0, 0, 0, 0, 1], dtype=np.uint8)

    combined = combine_labels_heterogeneous(wm, gm, CSF, skull, membranes)

    np.testing.assert_array_equal(combined, np.array([0, 1, 2, 3, 4, 5], dtype=np.uint8))


def test_combine_masks_heterogeneous_shape_mismatch():

    wm = np.array([1, 0, 0, 0, 0], dtype=np.uint8)
    gm = np.array([0, 0, 1, 0, 0, 0], dtype=np.uint8)
    CSF = np.array([0, 0, 0, 1, 0, 0], dtype=np.uint8)
    skull = np.array([0, 0, 0, 0, 1, 0], dtype=np.uint8)

    with pytest.raises(ValueError):
        combined = combine_labels_heterogeneous(wm, gm, CSF, skull)

def test_combine_masks_heterogeneous_with_membranes_shape_mismatch():

    wm = np.array([0, 1, 0, 0, 0, 0], dtype=np.uint8)
    gm = np.array([0, 0, 1, 0, 0, 0], dtype=np.uint8)
    CSF = np.array([0, 0, 0, 1, 0, 0], dtype=np.uint8)
    skull = np.array([0, 0, 0, 0, 1, 0], dtype=np.uint8)
    membranes = np.array([0, 0, 0, 0, 1], dtype=np.uint8)

    with pytest.raises(ValueError):
        combined = combine_labels_heterogeneous(wm, gm, CSF, skull, membranes)