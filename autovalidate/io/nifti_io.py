import numpy as np
import nibabel as nib
from pathlib import Path


def load_nifti(file_path: Path) -> tuple[np.ndarray, np.array]:

    """
    Loads a NIfTI image and returns the image array and affine

    Args:
        file_path : Path to the input file

    Returns:
        A tuple of the image array and affine matrix 
    """
 
    try:
        img = nib.load(file_path)
        img_data = img.get_fdata()

        return img_data.astype(np.int16), img.affine.astype(np.float64)

    except nib.filebasedimages.ImageFileError:
        raise ValueError("Please provide a valid NIfTI file")
    

def save_nifti(input_array: np.ndarray, affine_array: np.array, file_path: Path):

    """
    Saves the input array and affine in a specified file as a .nii.gz file

    Args:
        input_array : Input array of the mask
        affine_array : Input affine of the mask
        file_path : File path to be saved

    """

    file = nib.Nifti1Image(input_array,affine_array)
    
    nib.save(file,file_path)