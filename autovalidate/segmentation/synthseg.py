from pathlib import Path


# DEFINITION OF LABELS
SYNTHSEG_CSF_LABELS = [4, 5, 14, 15, 24, 43, 44]
SYNTHSEG_WM_LABELS = [2, 7, 41, 46]
SYNTHSEG_GM_LABELS = [3, 8, 10, 11, 12, 13, 16, 17, 18, 26, 28, 
             42, 47, 49, 50, 51, 52, 53, 54, 58, 60]
SYNTHSEG_BRAIN_EXCLUDE_LABELS = [0, 4, 5, 14, 15, 24, 43, 44]            

def create_synthseg_command(mri_synthseg_path: Path,
        t1_path: Path,
        target_dir: Path,
        extra_args: list[str] | None = None) -> list:

    """
    Returns a list containing the mri_synthseg command to be executed

    Args:
        mri_synthseg_path : Path to the mri_synthseg command
        t1_path : Path to the T1 image for segmentation
        target_dir : Path where SynthSeg output will be saved
        extra_args : List of extra arguments passed to the mri_synthseg command
    
    Returns:
        A list containing the command to run
    """

    file_name = Path(t1_path.stem).stem

    seg_out = target_dir / (file_name + "_SynthSeg.nii.gz")

    seg_cmd = [
            str(mri_synthseg_path),
            "--i", str(t1_path),
            "--o", str(seg_out),
            *(extra_args or []),
        ]
    
    return seg_cmd