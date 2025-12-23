from pathlib import Path
import os
from autovalidate.segmentation import extract_brain, extract_CSF, process_all_brain_csf_shells

# ===================== USER CONFIGURATION =====================
# Edit these variables for your environment before running.

# Directory of your study
# BASE = "path/to/your/study"


# Directory containing SynthSeg Output Segmented files
SYNTHSEG_OUTPUT_ROOT = os.path.join(BASE, "SynthSeg_Outputs")

# Directory where Brain files will be stored
BRAIN_OUTPUT_ROOT = os.path.join(BASE, "Extracted_Brains")

# Directory where CSF files will be stored
CSF_OUTPUT_ROOT = os.path.join(BASE, "Extracted_CSF")

# Directory where Skull files will be stored
SKULL_OUTPUT_ROOT = os.path.join(BASE, "Extracted_Skull")

# =================== END USER CONFIGURATION ===================


# 1) Per segmentation: extract brain and CSF masks
for file in os.listdir(SYNTHSEG_OUTPUT_ROOT):
    filename = os.fsdecode(file)
    if not filename.endswith(".gz"):
        continue
    full_path = os.path.join(SYNTHSEG_OUTPUT_ROOT, filename)
    extract_brain(full_path, BRAIN_OUTPUT_ROOT)
    extract_CSF(full_path, CSF_OUTPUT_ROOT)

# 2) After all masks exist, build skull (outer shell) masks
process_all_brain_csf_shells(
    brain_dir=BRAIN_OUTPUT_ROOT,
    csf_dir=CSF_OUTPUT_ROOT,
    out_dir=SKULL_OUTPUT_ROOT,
    thickness_vox=5,
    min_cc_size=10000,  # e.g. 5k–10k to drop small islands
)