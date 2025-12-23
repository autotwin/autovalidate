from pathlib import Path
import os
from autovalidate.morphology import process_one_subject

# ===================== USER CONFIGURATION =====================
# Edit these variables for your environment before running.

# Directory of your study
# BASE = "path/to/your/study"
BASE = "/projectnb/lejlab2/Evangelos_Practice/Autovalidate"

# Directory where Brain files are stored
BRAIN_OUTPUT_ROOT = os.path.join(BASE, "Extracted_Brains")

# Directory where CSF files are stored
CSF_OUTPUT_ROOT = os.path.join(BASE, "Extracted_CSF")

# Directory where Skull files are stored
SKULL_OUTPUT_ROOT = os.path.join(BASE, "Extracted_Skull")

# Directory where new files will be stored
NEW_FILES_OUTPUT_ROOT = os.path.join(BASE, "Inner_Layer_creation")
os.makedirs(NEW_FILES_OUTPUT_ROOT, exist_ok=True)

# =================== END USER CONFIGURATION ===================


if __name__ == "__main__":
    # infer subject roots from brain masks in BRAIN_DIR
    brain_files = sorted(
        f for f in os.listdir(BRAIN_OUTPUT_ROOT) if f.endswith("_brain_mask.nii.gz")
    )

    for bf in brain_files:
        subject_root = bf.replace("_brain_mask.nii.gz", "")
        process_one_subject(BRAIN_OUTPUT_ROOT,CSF_OUTPUT_ROOT,SKULL_OUTPUT_ROOT,NEW_FILES_OUTPUT_ROOT,subject_root)  