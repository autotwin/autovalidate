import os

from autovalidate.combine import combine_all_components

# ===================== USER CONFIGURATION =====================
# Edit these variables for your environment before running.

# Directory of your study
BASE = "path/to/study"

# Inputs
BRAIN_DIR = os.path.join(BASE, "Cleaned")
CSF_DIR   = os.path.join(BASE, "Cleaned")  # or your latest CSF dir
SKULL_DIR = os.path.join(BASE, "Cleaned")  # or your latest skull dir
ORIG_STRAIN_DIR = os.path.join(BASE, "Original_Strain_Scans")  # Define where original strain scans are stored

# Output
OUT_DIR   = os.path.join(BASE, "Final_Head")
os.makedirs(OUT_DIR, exist_ok=True)

# =================== END USER CONFIGURATION ===================

if __name__ == "__main__":
    # infer subject roots from brain masks
    brain_files = sorted(
        f for f in os.listdir(BRAIN_DIR)
        if f.endswith("_brain_clean.nii.gz")
    )

    for bf in brain_files:
        subj_root = bf.replace("_brain_clean.nii.gz", "")
        combine_all_components(BRAIN_DIR, CSF_DIR, SKULL_DIR, ORIG_STRAIN_DIR, OUT_DIR, subj_root)