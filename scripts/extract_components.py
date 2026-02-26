from pathlib import Path
import os
from autovalidate.segmentation import process_all_brain_csf_skulls

BASE = "path/to/study"

SYNTHSEG_OUTPUT_ROOT = os.path.join(BASE, "SynthSeg_Outputs")
BRAIN_OUTPUT_ROOT     = os.path.join(BASE, "Extracted_Brains")
CSF_OUTPUT_ROOT       = os.path.join(BASE, "Extracted_CSF")
SKULL_OUTPUT_ROOT     = os.path.join(BASE, "Extracted_Skull")

SKULL_THICKNESS_VOX = 6

process_all_brain_csf_skulls(
    synthseg_root=SYNTHSEG_OUTPUT_ROOT,
    brain_out=BRAIN_OUTPUT_ROOT,
    csf_out=CSF_OUTPUT_ROOT,
    skull_out=SKULL_OUTPUT_ROOT,
    thickness_voxels=SKULL_THICKNESS_VOX,
    min_cc_size=10000,
)
