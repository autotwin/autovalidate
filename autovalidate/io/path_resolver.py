from pathlib import Path

def path_resolving(source_dir: Path, algorithm: str | None = None, include_membranes: bool | None = None) -> dict:

    """
    Searches for the corresponding files of T1 Image, 
    SLANT-CRUISE Segmentation algorithm, Falx and Tentorium masks.

    Args:
        source_dir : Directory to search for the files
        algorithm : Which algorithm will be used
        include_membranes : Are membranes (Falx & Tentorium) included in the simulation?
    
    Returns:
        A dict (t1, slant_seg, falx, tentorium) containing the paths for each file
    """
    
    if not source_dir.exists():
        raise FileNotFoundError(f"Path does not exist: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {source_dir}")

    matches = list(source_dir.glob("*register_to_tMRI"))
    if not matches:
        raise FileNotFoundError(f"register_to_tMRI subdirectory not found in: {source_dir}")
    reg_dir = matches[0]    

    t1_matches = list(reg_dir.glob("*_tMRIreg_T1.nii.gz"))
    if not t1_matches:
        raise FileNotFoundError(f"T1 file not found in: {reg_dir}")
    T1_file = t1_matches[0]
        
    if algorithm == "slant":
        macruise_matches = list(reg_dir.glob("*_tMRIreg_macruise.nii.gz"))
        if not macruise_matches:
            raise FileNotFoundError(f"Segmentation file not found in: {reg_dir}")
        macruise_file = macruise_matches[0]
    else:
        macruise_file = None

    if include_membranes:
        falx_matches = list(reg_dir.glob("*_tMRIreg_falx.nii.gz"))
        if not falx_matches:
            raise FileNotFoundError(f"Falx file not found in: {reg_dir}")
        falx_file = falx_matches[0]

        tentorium_matches = list(reg_dir.glob("*_tMRIreg_tentorium.nii.gz"))
        if not tentorium_matches:
            raise FileNotFoundError(f"Tentorium file not found in: {reg_dir}")
        tentorium_file = tentorium_matches[0]
    else:
        falx_file = None
        tentorium_file = None
    
    paths_dict = {
        "t1":        T1_file,
        "slant_seg": macruise_file,
        "falx":      falx_file,
        "tentorium": tentorium_file,
    }
    
    return paths_dict