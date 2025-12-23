import os

from autovalidate.combine import combine_all_components

# ===================== USER CONFIGURATION =====================
# Edit these variables for your environment before running.

# Directory of your study
#BASE = "path/to/study"
BASE = "/projectnb/lejlab2/Evangelos_Practice/Autovalidate"

# Inputs
BRAIN_DIR = os.path.join(BASE, "Extracted_Brains")
CSF_DIR   = os.path.join(BASE, "Inner_Layer_creation")  # or your latest CSF dir
SKULL_DIR = os.path.join(BASE, "Inner_Layer_creation")  # or your latest skull dir

# Output
OUT_DIR   = os.path.join(BASE, "Final_Head")
os.makedirs(OUT_DIR, exist_ok=True)

# =================== END USER CONFIGURATION ===================

if __name__ == "__main__":
    # infer subject roots from brain masks
    brain_files = sorted(
        f for f in os.listdir(BRAIN_DIR)
        if f.endswith("_tMRIreg_T1_SynthSeg_brain_mask.nii.gz")
    )

    for bf in brain_files:
        subj_root = bf.replace("_tMRIreg_T1_SynthSeg_brain_mask.nii.gz", "")
        combine_all_components(BRAIN_DIR, CSF_DIR, SKULL_DIR, OUT_DIR, subj_root)