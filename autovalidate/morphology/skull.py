import numpy as np
from scipy.ndimage import binary_dilation, generate_binary_structure
from skimage.morphology import ball
from skimage.measure import label

def create_skull(brain_mask: np.array, csf_mask: np.array) -> np.array:

    """
    Create a skull mask as an outward shell around the combined brain+CSF mask

    Args:
        brain_mask : np.array containing the brain mask
        csf_mask : np.array containing the csf mask
    
    Returns:
        Returns a uint8 np.array of the same shape as the    
        input masks, where 1 indicates a skull voxel
    """

    if not (brain_mask.shape == csf_mask.shape):
        raise ValueError("All masks must have the same shape")
    
    combined = (brain_mask | csf_mask)

    struct = ball(3)
    outer = binary_dilation(combined, structure=struct)

    skull = outer & ~combined

    skull = skull.astype(np.uint8)

    return skull


def remove_small_components(mask: np.array, min_size: int) -> np.array:

    """
    Removes small components from the mask and assigns them to background
    Keeps only connected components with at least min_size voxels.

    Args:
        mask : Input mask to check for small components
        min_size : Minimum number of voxels that the component should have

    Returns: 
        Mask cleaned from small components
    """

    if min_size <= 0:
        raise ValueError("Minimum Size should be a positive integer value")
    
    labels = label(mask, connectivity=1)
    counts = np.bincount(labels.ravel())

    counts[0] = 0 
    keep = np.where(counts >= min_size)[0]
    cleaned = np.isin(labels, keep)

    cleaned = cleaned.astype(np.uint8)
    return cleaned


def ensure_no_brain_skull_contact(brain_mask: np.array, skull_mask: np.array, csf_mask: np.array) -> tuple[np.ndarray, np.ndarray]:

    """
    Guarantee that no brain voxel is adjacent to any skull voxel
    (26-connectivity) by iteratively converting contact skull voxels to CSF.

    Args:
        brain_mask : np.ndarray, binary brain mask (unchanged on output).
        skull_mask : np.ndarray, binary skull mask.
        csf_mask : np.ndarray, binary CSF mask.
    
    Returns
        new_csf : np.ndarray (uint8)
        new_skull : np.ndarray (uint8)
    """

    if not (brain_mask.shape == skull_mask.shape == csf_mask.shape):
        raise ValueError("All masks must have the same shape")

    max_iterations = 50
    
    brain = brain_mask.astype(bool)
    skull = skull_mask.astype(bool)
    csf = csf_mask.astype(bool)

    # 26-connectivity structuring element (faces + edges + corners)
    struct = generate_binary_structure(3, 3)

    for _ in range(max_iterations):
        brain_neighborhood = binary_dilation(brain, structure=struct)
        contact = skull & brain_neighborhood
        n_contact = np.count_nonzero(contact)

        if n_contact == 0:
            break

        csf = csf | contact
        skull = skull & ~contact

    return csf.astype(np.uint8), skull.astype(np.uint8)