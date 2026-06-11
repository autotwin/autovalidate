import numpy as np

def extract_mask(seg_array: np.array, labels: list, exclude: bool) -> np.array:

    """
    Extracts the components specified as a mask

    Args:
        seg_array : np.array containing integer labels identifying the          
                    anatomical structure at each voxel  
        labels : List of integer labels to include or exclude. 
                 An empty list returns all zeros (include mode)
                 or all ones (exclude mode)
        exclude : If True, returns 1 for every voxel that does not belong 
                  to the specified labels. 
                  If False, returns 1 for every voxel that belongs to
                  the specified labels.
    
    Returns: 
        Returns a uint8 numpy array of the same shape as seg_array, 
        where 1 indicates the voxel belongs to (include mode) 
        or does not belong to (exclude mode) the specified labels.
    """

    if exclude == True:
        mask = ~np.isin(seg_array, labels)
    else:
        mask = np.isin(seg_array, labels)
    
    mask = mask.astype(np.uint8)

    return mask