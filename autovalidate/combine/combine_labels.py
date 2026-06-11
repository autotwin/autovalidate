import numpy as np


def _assign_labels(wm: np.ndarray, gm: np.ndarray, csf: np.ndarray, skull: np.ndarray, membranes: np.ndarray) -> np.ndarray:

    """
    Helper Function which creates a mask with all individual masks combined
    Labels: 0 [background], 1 [Brain], 3 [CSF], 4 [Skull], 5 [Membranes]

    Args:
        wm : White Matter Mask | np.ndarray (uint8)
        gm : Gray Matter Mask | np.ndarray (uint8)
        csf : CSF Mask | np.ndarray (uint8)
        skull : Skull Mask | np.ndarray (uint8)
        membranes : Falx & Tentorium Mask | np.ndarray (uint8)

    Returns:
        A combined mask with the corresponding labels
    """

    labels = np.zeros(wm.shape, dtype=np.uint8)
    labels[wm.astype(bool)] = 1
    labels[gm.astype(bool)] = 2
    labels[csf.astype(bool)] = 3
    labels[skull.astype(bool)] = 4
    labels[membranes.astype(bool)] = 5
    
    return labels


def combine_labels_homogeneous(brain: np.ndarray, csf: np.ndarray, skull: np.ndarray, membranes: np.ndarray | None = None) -> np.ndarray:

    """
    All individual masks combined into 1 mask (Homogeneous Brain case)

    Args:
        brain : Brain Mask | np.ndarray (uint8)
        csf : CSF Mask | np.ndarray (uint8)
        skull : Skull Mask | np.ndarray (uint8)
        membranes (Optional) : Falx & Tentorium Mask | np.ndarray (uint8)

    Returns:
        A combined mask with the corresponding labels
    """

    if not (brain.shape == csf.shape == skull.shape):
        raise ValueError("All masks must have the same shape")

    gm = np.zeros_like(brain)
    
    if membranes is not None:
        if membranes.shape != brain.shape:
            raise ValueError("All masks must have the same shape")
        combined_labels = _assign_labels(brain, gm, csf, skull, membranes)
    else:
        membranes = np.zeros_like(brain)
        combined_labels = _assign_labels(brain, gm, csf, skull, membranes)

    return combined_labels


def combine_labels_heterogeneous(wm: np.ndarray, gm: np.ndarray, csf: np.ndarray, skull: np.ndarray, membranes: np.ndarray | None = None) -> np.ndarray:

    """
    All individual masks combined into 1 mask (Heterogeneous Brain case)

    Args:
        wm : White Matter Mask | np.ndarray (uint8)
        gm : Gray Matter Mask | np.ndarray (uint8)
        csf : CSF Mask | np.ndarray (uint8)
        skull : Skull Mask | np.ndarray (uint8)
        membranes (Optional) : Falx & Tentorium Mask | np.ndarray (uint8)

    Returns:
        A combined mask with the corresponding labels
    """

    if not (wm.shape == gm.shape == csf.shape == skull.shape):
        raise ValueError("All masks must have the same shape")
    
    if membranes is not None:
        if membranes.shape != wm.shape:
            raise ValueError("All masks must have the same shape")
        combined_labels = _assign_labels(wm, gm, csf, skull, membranes)
    else:
        membranes = np.zeros_like(wm)
        combined_labels = _assign_labels(wm, gm, csf, skull, membranes)

    return combined_labels