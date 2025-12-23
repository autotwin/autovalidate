import os
from pathlib import Path

from autovalidate.pipeline import run_synthseg_and_resample_strain

# ===================== USER CONFIGURATION =====================

# Directory of your study
BASE = "path/to/your/study"

# Directory where T1 scans are stored 
T1_ROOT = os.path.join(BASE, "Original_T1_Scans")

# Directory where strains scans are stored
STRAIN_ROOT = os.path.join(BASE, "Original_Strain_Scans")

# Directory where SynthSeg output files will be stored
SYNTHSEG_OUTPUT_ROOT = os.path.join(BASE, "SynthSeg_Outputs")

# Directory where resampled strain scans files will be stored
RESAMPLED_STRAIN_ROOT = os.path.join(BASE, "Resampled_Strain_Scans")

# Define the installation directory of mri_synthseg and mri_convert (you can find them by calling
# which mri_synthseg and which mri_convert)
MRI_SYNTHSEG_PATH = Path("/share/pkg.8/freesurfer/7.4.1_CentOS-8/install/freesurfer/bin/mri_synthseg")
MRI_CONVERT_PATH = Path("/share/pkg.8/freesurfer/7.4.1_CentOS-8/install/freesurfer/bin/mri_convert")

EXTRA_ARGS: list[str] = []

# =================== END USER CONFIGURATION ===================

def main() -> None:
    run_synthseg_and_resample_strain(
        t1_root=T1_ROOT,
        strain_root=STRAIN_ROOT,
        synthseg_root=SYNTHSEG_OUTPUT_ROOT,
        resampled_strain_root=RESAMPLED_STRAIN_ROOT,
        mri_synthseg_path=MRI_SYNTHSEG_PATH,
        mri_convert_path=MRI_CONVERT_PATH,
        extra_args=EXTRA_ARGS,
    )

if __name__ == "__main__":
    main()
