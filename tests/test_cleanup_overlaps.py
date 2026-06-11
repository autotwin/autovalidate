import numpy as np
import pytest

from autovalidate.cleanup.overlaps import resolve_overlaps, resolve_membrane_priority

def test_cleanup_no_overlaps():

    WM= np.array([1, 0, 0, 0], dtype=np.uint8)
    GM=np.array([0, 1, 0, 0], dtype=np.uint8)
    CSF=np.array([0, 0, 1, 0], dtype=np.uint8)
    skull=np.array([0, 0, 0, 1], dtype=np.uint8)

    new_WM, new_GM, new_CSF, new_Skull = resolve_overlaps(WM, GM, CSF, skull)

    np.testing.assert_array_equal(WM, new_WM)
    np.testing.assert_array_equal(GM, new_GM)
    np.testing.assert_array_equal(CSF, new_CSF)
    np.testing.assert_array_equal(skull, new_Skull)

def test_cleanup_gm_overlaps_wm():

    WM= np.array([1, 0, 0, 0], dtype=np.uint8)
    GM=np.array([1, 0, 0, 0], dtype=np.uint8)
    CSF=np.array([0, 0, 1, 0], dtype=np.uint8)
    skull=np.array([0, 0, 0, 1], dtype=np.uint8)

    new_WM, new_GM, new_CSF, new_Skull = resolve_overlaps(WM, GM, CSF, skull)

    np.testing.assert_array_equal(WM, new_WM)
    np.testing.assert_array_equal(new_GM, np.array([0,0,0,0], dtype=np.uint8))
    np.testing.assert_array_equal(CSF, new_CSF)
    np.testing.assert_array_equal(skull, new_Skull)  


def test_cleanup_csf_overlaps_wm():

    WM= np.array([1, 0, 0, 0], dtype=np.uint8)
    GM=np.array([0, 1, 0, 0], dtype=np.uint8)
    CSF=np.array([1, 0, 0, 0], dtype=np.uint8)
    skull=np.array([0, 0, 0, 1], dtype=np.uint8)

    new_WM, new_GM, new_CSF, new_Skull = resolve_overlaps(WM, GM, CSF, skull)

    np.testing.assert_array_equal(WM, new_WM)
    np.testing.assert_array_equal(GM, new_GM)
    np.testing.assert_array_equal(new_CSF, np.array([0,0,0,0], dtype=np.uint8))
    np.testing.assert_array_equal(skull, new_Skull)  

def test_cleanup_skull_overlaps_wm():

    WM= np.array([1, 0, 0, 0], dtype=np.uint8)
    GM=np.array([0, 1, 0, 0], dtype=np.uint8)
    CSF=np.array([0, 0, 1, 0], dtype=np.uint8)
    skull=np.array([1, 0, 0, 0], dtype=np.uint8)

    new_WM, new_GM, new_CSF, new_skull = resolve_overlaps(WM, GM, CSF, skull)

    np.testing.assert_array_equal(WM, new_WM)
    np.testing.assert_array_equal(GM, new_GM)
    np.testing.assert_array_equal(CSF, new_CSF)
    np.testing.assert_array_equal(new_skull, np.array([0,0,0,0], dtype=np.uint8))  

def test_cleanup_csf_overlaps_gm():

    WM= np.array([1, 0, 0, 0], dtype=np.uint8)
    GM=np.array([0, 1, 0, 0], dtype=np.uint8)
    CSF=np.array([0, 1, 0, 0], dtype=np.uint8)
    skull=np.array([0, 0, 0, 1], dtype=np.uint8)

    new_WM, new_GM, new_CSF, new_skull = resolve_overlaps(WM, GM, CSF, skull)

    np.testing.assert_array_equal(WM, new_WM)
    np.testing.assert_array_equal(GM, new_GM)
    np.testing.assert_array_equal(new_CSF, np.array([0,0,0,0], dtype=np.uint8))
    np.testing.assert_array_equal(skull, new_skull)  

def test_cleanup_skull_overlaps_gm():

    WM= np.array([1, 0, 0, 0], dtype=np.uint8)
    GM=np.array([0, 1, 0, 0], dtype=np.uint8)
    CSF=np.array([0, 0, 1, 0], dtype=np.uint8)
    skull=np.array([0, 1, 0, 0], dtype=np.uint8)

    new_WM, new_GM, new_CSF, new_skull = resolve_overlaps(WM, GM, CSF, skull)

    np.testing.assert_array_equal(WM, new_WM)
    np.testing.assert_array_equal(GM, new_GM)
    np.testing.assert_array_equal(CSF, new_CSF)
    np.testing.assert_array_equal(new_skull, np.array([0,0,0,0], dtype=np.uint8))  

def test_cleanup_skull_overlaps_CSF():

    WM= np.array([1, 0, 0, 0], dtype=np.uint8)
    GM=np.array([0, 1, 0, 0], dtype=np.uint8)
    CSF=np.array([0, 0, 1, 0], dtype=np.uint8)
    skull=np.array([0, 0, 1, 0], dtype=np.uint8)

    new_WM, new_GM, new_CSF, new_skull = resolve_overlaps(WM, GM, CSF, skull)

    np.testing.assert_array_equal(WM, new_WM)
    np.testing.assert_array_equal(GM, new_GM)
    np.testing.assert_array_equal(CSF, new_CSF)
    np.testing.assert_array_equal(new_skull, np.array([0,0,0,0], dtype=np.uint8))

def test_cleanup_4_overlaps():

    WM= np.array([1, 0, 0, 0], dtype=np.uint8)
    GM=np.array([1, 0, 0, 0], dtype=np.uint8)
    CSF=np.array([1, 0, 0, 0], dtype=np.uint8)
    skull=np.array([1, 0, 0, 0], dtype=np.uint8)

    new_WM, new_GM, new_CSF, new_skull = resolve_overlaps(WM, GM, CSF, skull)

    np.testing.assert_array_equal(WM, new_WM)
    np.testing.assert_array_equal(new_GM, np.array([0,0,0,0], dtype=np.uint8))
    np.testing.assert_array_equal(new_CSF, np.array([0,0,0,0], dtype=np.uint8))
    np.testing.assert_array_equal(new_skull, np.array([0,0,0,0], dtype=np.uint8))

def test_cleanup_shape_mismatch():

    WM= np.array([1, 0, 0, 0], dtype=np.uint8)
    GM=np.array([0, 1, 0, 0], dtype=np.uint8)
    CSF=np.array([0, 0, 1, 0], dtype=np.uint8)
    skull=np.array([0, 0, 0], dtype=np.uint8)

    with pytest.raises(ValueError):
        new_WM, new_GM, new_CSF, new_skull = resolve_overlaps(WM, GM, CSF, skull)


def test_membranes_cleanup_overlaps():

    membranes = np.array([1, 0, 0, 0, 0], dtype=np.uint8)
    wm = np.array([1, 1, 0, 0, 0], dtype=np.uint8)
    gm =np.array([1, 0, 1, 0, 0], dtype=np.uint8)
    csf = np.array([1, 0, 0, 1, 0], dtype=np.uint8)
    skull = np.array([1, 0, 0, 0, 1], dtype=np.uint8)

    new_membranes, new_wm, new_gm, new_csf, new_skull = resolve_membrane_priority(membranes, wm, gm, csf, skull)

    np.testing.assert_array_equal(new_membranes, membranes)
    np.testing.assert_array_equal(new_wm, np.array([0, 1, 0, 0, 0], dtype=np.uint8))
    np.testing.assert_array_equal(new_gm, np.array([0, 0, 1, 0, 0], dtype=np.uint8))
    np.testing.assert_array_equal(new_csf, np.array([0, 0, 0, 1, 0], dtype=np.uint8))
    np.testing.assert_array_equal(new_skull, np.array([0, 0, 0, 0, 1], dtype=np.uint8))

def test_membranes_cleanup_no_overlaps():

    membranes = np.array([1, 0, 0, 0, 0], dtype=np.uint8)
    wm = np.array([0, 1, 0, 0, 0], dtype=np.uint8)
    gm =np.array([0, 0, 1, 0, 0], dtype=np.uint8)
    csf = np.array([0, 0, 0, 1, 0], dtype=np.uint8)
    skull = np.array([0, 0, 0, 0, 1], dtype=np.uint8)

    new_membranes, new_wm, new_gm, new_csf, new_skull = resolve_membrane_priority(membranes, wm, gm, csf, skull)

    np.testing.assert_array_equal(new_membranes, membranes)
    np.testing.assert_array_equal(new_wm, wm)
    np.testing.assert_array_equal(new_gm, gm)
    np.testing.assert_array_equal(new_csf, csf)
    np.testing.assert_array_equal(new_skull, skull)

def test_membranes_cleanup_shape_mismatch():

    membranes = np.array([0, 0, 0, 0], dtype=np.uint8)
    wm = np.array([0, 1, 0, 0, 0], dtype=np.uint8)
    gm =np.array([0, 0, 1, 0, 0], dtype=np.uint8)
    csf = np.array([0, 0, 0, 1, 0], dtype=np.uint8)
    skull = np.array([0, 0, 0, 0, 1], dtype=np.uint8)

    with pytest.raises(ValueError):
        new_membranes, new_wm, new_gm, new_csf, new_skull = resolve_membrane_priority(membranes, wm, gm, csf, skull)
