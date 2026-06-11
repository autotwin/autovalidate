import numpy as np
from pathlib import Path

def save_npy(input_array: np.array, file_path: Path):

    """
    Saves the input array in a specified file as .npy file

    Args:
        input_array : Input array of the mask
        file_path : File path to be saved

    """

    np.save(file_path, input_array)