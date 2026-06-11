from dataclasses import dataclass

@dataclass
class Config:
    algorithm: str
    brain_fidelity: str
    include_membranes: bool
    subject_dir: str
    output_dir: str
    subject_id: str
    motion_type: str
    keep_intermediate_files: bool
    mri_synthseg: str | None
    mri_convert: str | None
    bet: str | None
    fast: str | None

def parse_config(raw_dict: dict) -> Config:

    """
    Parses and validates a raw config dict (as produced by tomllib) 
    and returns a Config dataclass. Raises ValueError if required 
    fields are missing or have invalid values.

    Args:
        raw_dict : A dict containing all the keywords to be passed in the config file

    Returns:
        A Config dataclass
    """

    if 'env' not in raw_dict:
        raise ValueError("Input Dict does not have the correct structure")
    
    if 'run' not in raw_dict:
        raise ValueError("Input Dict does not have the correct structure")

    if "subject_dir" not in raw_dict["run"]:
        raise ValueError("Subject Directory is not specified")

    if "output_dir" not in raw_dict["run"]:
        raise ValueError("Output Directory is not specified")

    if "subject_id" not in raw_dict["run"]:
        raise ValueError("Subject ID has not been provided")

    if "motion_type" not in raw_dict["run"]:
        raise ValueError("Motion type has not been provided")

    motion_type = raw_dict["run"]["motion_type"].upper()
    if motion_type not in {"NR", "NE"}:
        raise ValueError("Wrong motion type! Please select NR or NE")

    algorithm = raw_dict["run"]["algorithm"].lower()
    if algorithm not in {"synthseg", "fsl", "slant"}:
        raise ValueError("Wrong Segmentation Algorithm! Please select SynthSeg, FSL or SLANT")

    brain_fidelity = raw_dict["run"]["brain_fidelity"].lower()        
    if brain_fidelity not in {"homogeneous", "heterogeneous", }:
            raise ValueError("Wrong Fidelity Level! Please select either Homogeneous or Heterogeneous")

    include_membranes = raw_dict["run"]["include_membranes"]
    if not isinstance(include_membranes, bool):
        raise ValueError("Wrong include membrane boolean! Please select either True or False")

    if include_membranes and "mri_convert" not in raw_dict["env"]:
        raise ValueError("mri_convert path required when include_membranes = true")

    if algorithm == "synthseg":
        if "mri_synthseg" not in raw_dict["env"]:
            raise ValueError("mri_synthseg path not specified!")
        if "mri_convert" not in raw_dict["env"]:
            raise ValueError("mri_convert path not specified!")
 
    if algorithm == "fsl":
        if "bet" not in raw_dict["env"]:
            raise ValueError("bet path not specified!")
        if "fast" not in raw_dict["env"]:
            raise ValueError("fast path not specified!")
    
    keep_intermediate_files = raw_dict["run"].get("keep_intermediate_files", False)
    if not isinstance(keep_intermediate_files, bool):
        raise ValueError("Wrong keep_intermediate_files boolean! Please select either True or False")

    return Config(
        algorithm = algorithm,
        brain_fidelity = brain_fidelity,
        include_membranes = include_membranes,
        subject_dir = raw_dict["run"]["subject_dir"],
        output_dir = raw_dict["run"]["output_dir"],
        subject_id = raw_dict["run"]["subject_id"],
        motion_type = motion_type,
        keep_intermediate_files = keep_intermediate_files,
        mri_synthseg = raw_dict["env"].get("mri_synthseg"),
        mri_convert  = raw_dict["env"].get("mri_convert"),
        bet          = raw_dict["env"].get("bet"),
        fast         = raw_dict["env"].get("fast"),
    )
