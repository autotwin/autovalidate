from pathlib import Path

def filename_building(subject_id: str, motion_type: str, algorithm: str, brain_fidelity: str, membranes: bool, mask_type: str):

    """
    Given a set of keywords, the output filename is created

    Args:
        subject_id: Corresponding subject's ID
        motion_type : Motion type (NR or NE)
        algorithm : Which algorithm will be used
        brain_fidelity : Fidelity of the model (Homogeneous or Heterogeneous)
        membranes : Include or Exclude membranes
        mask_type : Which mask is saved in this file

    Returns:
        The complete filename of the file separating keywords with '-'
    """

    if membranes == True:
        membranes_name = "membranesON"
    else:
        membranes_name = "membranesOFF"

    keywords = [subject_id, motion_type, algorithm, brain_fidelity, membranes_name, mask_type]

    filename = '-'.join(keywords)

    if mask_type == "combined":
        full_filename = f"{filename}.npy"
    else:
        full_filename = f"{filename}.nii.gz"

    return full_filename

