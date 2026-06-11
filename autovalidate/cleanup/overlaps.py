import numpy as np

def resolve_overlaps(wm: np.array, gm: np.array, csf: np.array, skull: np.array) -> tuple[np.ndarray, np.ndarray,np.ndarray, np.ndarray]:

    """
    Cleans the masks and ensures no overlaps between masks
    Hierarchy: White Matter > Gray Matter > CSF > Skull

    Args:
        wm : White Matter mask
        gm : Gray Matter mask
        csf : CSF mask
        skull : Skull mask
    
    Returns:
        wm_clean : np.ndarray (uint8)
        gm_clean : np.ndarray (uint8)
        csf_clean : np.ndarray (uint8)
        skull_clean : np.ndarray (uint8)
    """

    if not (wm.shape == gm.shape == skull.shape == csf.shape):
        raise ValueError("All masks must have the same shape")

    wm_clean = wm.copy()
    gm_clean = gm.copy()
    skull_clean = skull.copy()
    csf_clean   = csf.copy()    
    
    # WM wins over GM, CSF and Skull
    gm_clean[wm_clean.astype(bool)] = False
    csf_clean[wm_clean.astype(bool)] = False
    skull_clean[wm_clean.astype(bool)] = False

    # GM wins over CSF and Skull
    csf_clean[gm_clean.astype(bool)] = False
    skull_clean[gm_clean.astype(bool)] = False

    # CSF wins over Skull
    skull_clean[csf_clean.astype(bool)] = False

    return wm_clean.astype(np.uint8), gm_clean.astype(np.uint8), csf_clean.astype(np.uint8), skull_clean.astype(np.uint8)



def resolve_membrane_priority(membranes: np.array, wm: np.array, gm: np.array, csf: np.array, skull: np.array) -> tuple[np.ndarray, np.ndarray, np.ndarray,np.ndarray, np.ndarray]:

    """
    Cleans the masks and ensures no overlaps between masks
    Hierarchy: Membranes > White Matter > Gray Matter > CSF > Skull

    Args:
        membranes : Falx & Tentorium masks
        wm : White Matter mask
        gm : Gray Matter mask
        csf : CSF mask
        skull : Skull mask
    
    Returns:
        membranes_clean : np.ndarray (uint8)
        wm_clean : np.ndarray (uint8)
        gm_clean : np.ndarray (uint8)
        csf_clean : np.ndarray (uint8)
        skull_clean : np.ndarray (uint8)
    """

    if not (membranes.shape == wm.shape == gm.shape == skull.shape == csf.shape):
        raise ValueError("All masks must have the same shape")

    membranes_clean = membranes.copy()
    wm_clean = wm.copy()
    gm_clean = gm.copy()
    skull_clean = skull.copy()
    csf_clean   = csf.copy()

    # Membranes win over everything
    wm_clean[membranes_clean.astype(bool)] = False
    gm_clean[membranes_clean.astype(bool)] = False
    csf_clean[membranes_clean.astype(bool)] = False
    skull_clean[membranes_clean.astype(bool)] = False

    return membranes_clean.astype(np.uint8), wm_clean.astype(np.uint8), gm_clean.astype(np.uint8), csf_clean.astype(np.uint8), skull_clean.astype(np.uint8)