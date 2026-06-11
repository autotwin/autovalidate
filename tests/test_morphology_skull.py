import numpy as np
import pytest

from autovalidate.morphology.skull import create_skull, remove_small_components, ensure_no_brain_skull_contact


def test_create_skull():

    brain_mask = np.zeros((9,9,9), dtype = np.uint8)
    brain_mask[4,4,4] = 1

    csf_mask = np.zeros((9,9,9), dtype = np.uint8)

    combined_mask = brain_mask | csf_mask

    skull_mask = create_skull(brain_mask, csf_mask)

    assert skull_mask.dtype == np.uint8
    assert np.sum(skull_mask & combined_mask) == 0 
    assert np.count_nonzero(skull_mask) > 0


def test_create_skull_size_mismatch():

    brain_mask = np.zeros((9,9,9), dtype = np.uint8)
    brain_mask[4,4,4] = 1

    csf_mask = np.zeros((8,8,8), dtype = np.uint8)

    with pytest.raises(ValueError):
        skull_mask = create_skull(brain_mask, csf_mask)


def test_remove_small_components():

    whole_mask = np.zeros((5,5,5), dtype = np.uint8)
    whole_mask[:3,:3,:3] = 1
    whole_mask[4,4,4] = 1

    cleaned = remove_small_components(whole_mask, min_size=10)

    assert cleaned[4,4,4] == 0
    np.testing.assert_array_equal(cleaned[:3,:3,:3], whole_mask[:3,:3,:3])


def test_remove_small_components_negative_min_size():

    whole_mask = np.zeros((5,5,5), dtype = np.uint8)
    whole_mask[:3,:3,:3] = 1
    whole_mask[4,4,4] = 1

    min_size = -10

    with pytest.raises(ValueError):
        cleaned = remove_small_components(whole_mask, min_size)


def test_ensure_no_brain_skull_contact():

    brain_mask = np.zeros((3,3,3), dtype=np.uint8)
    brain_mask[1,1,1] = 1

    skull_mask = np.zeros((3,3,3), dtype=np.uint8)
    skull_mask[2,1,1] = 1

    csf_mask = np.zeros((3,3,3), dtype=np.uint8)

    new_csf_mask, new_skull_mask = ensure_no_brain_skull_contact(brain_mask, skull_mask, csf_mask)

    assert new_skull_mask[2,1,1] == 0
    assert new_csf_mask[2,1,1] == 1
