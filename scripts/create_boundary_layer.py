from pathlib import Path
import os

from autovalidate.morphology import process_one_subject


# ===================== USER CONFIGURATION =====================

# Directory of your study
BASE = "/projectnb/lejlab2/Evangelos_Practice/Test_Autovalidate"

# Directory where Brain files are stored
BRAIN_OUTPUT_ROOT = os.path.join(BASE, "Extracted_Brains")

# Directory where CSF files are stored
CSF_OUTPUT_ROOT = os.path.join(BASE, "Extracted_CSF")

# Directory where Skull files are stored
SKULL_OUTPUT_ROOT = os.path.join(BASE, "Extracted_Skull")

# Directory where new files will be stored
NEW_FILES_OUTPUT_ROOT = os.path.join(BASE, "Inner_Layer_creation")
os.makedirs(NEW_FILES_OUTPUT_ROOT, exist_ok=True)

# User-defined thickness (in voxels) of the inner skull layer added to CSF
INNER_LAYER_THICKNESS_VOX = 3

# =================== END USER CONFIGURATION ===================


if __name__ == "__main__":
    # Infer subject roots from brain masks in BRAIN_OUTPUT_ROOT
    brain_files = sorted(
        f for f in os.listdir(BRAIN_OUTPUT_ROOT) if f.endswith("_brain_mask.nii.gz")
    )

    for bf in brain_files:
        subject_root = bf.replace("_brain_mask.nii.gz", "")
        process_one_subject(
            brain_dir=BRAIN_OUTPUT_ROOT,
            csf_dir=CSF_OUTPUT_ROOT,
            skull_dir=SKULL_OUTPUT_ROOT,
            out_dir=NEW_FILES_OUTPUT_ROOT,
            subject_root=subject_root,
            inner_thickness_voxels=INNER_LAYER_THICKNESS_VOX,
        )
