import os
import nibabel as nib
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.ndimage import (
    binary_erosion,
    binary_dilation,
    binary_closing, binary_fill_holes,
    generate_binary_structure,
)
from skimage.morphology import ball

def process_one_subject(BRAIN_DIR,CSF_DIR,SKULL_DIR,OUT_DIR,subject_root):
    """
    subject_root example:
        U01_HJF_0006_01_tMRIreg_T1_SynthSeg

    Expected files:
        BRAIN_DIR / subject_root + "_brain_mask.nii.gz"
        CSF_DIR   / subject_root + "_CSF_mask.nii.gz"
        SKULL_DIR / subject_root + "_braincsf_outer_shell.nii.gz"
    """
    brain_file = os.path.join(BRAIN_DIR, subject_root + "_brain_mask.nii.gz")
    csf_file   = os.path.join(CSF_DIR,   subject_root + "_CSF_mask.nii.gz")
    skull_file = os.path.join(SKULL_DIR, subject_root + "_braincsf_outer_shell.nii.gz")

    if not os.path.exists(brain_file):
        print("Missing brain:", brain_file)
        return
    if not os.path.exists(csf_file):
        print("Missing CSF:", csf_file)
        return
    if not os.path.exists(skull_file):
        print("Missing skull:", skull_file)
        return

    print("\n=== Subject:", subject_root, "===")
    print("brain:", brain_file)
    print("csf:", csf_file)
    print("skull:", skull_file)

    # ---- load masks ----
    skull_img = nib.load(skull_file)
    csf_img   = nib.load(csf_file)
    brain_img = nib.load(brain_file)

    skull = skull_img.get_fdata().astype(bool)
    csf   = csf_img.get_fdata().astype(bool)
    brain = brain_img.get_fdata().astype(bool)

    if not (skull.shape == csf.shape == brain.shape):
        print("Shape mismatch; skipping", subject_root)
        return

    print("skull shape:", skull.shape)
    print("csf shape: ", csf.shape)
    print("brain shape:", brain.shape)

    conn = generate_binary_structure(3, 2)  # 26-connectivity

    # ---- inside mask (brain + CSF) ----
    inside = brain | csf

    # ---- skullâ€“(brain+CSF) 1-voxel interface ----
    skull_eroded   = binary_erosion(skull, structure=conn)
    skull_boundary = skull & ~skull_eroded

    inside_dilated = binary_dilation(inside, structure=conn)

    inner_layer = skull_boundary & inside_dilated

    print("boundary voxels:", np.count_nonzero(skull_boundary))
    print("inner-layer voxels:", np.count_nonzero(inner_layer))

    # ---- move inner_layer: skull -> CSF ----
    skull_new = skull & ~inner_layer
    csf_new   = csf | inner_layer

    overlap = skull_new & csf_new
    print("overlap voxels after move:", np.count_nonzero(overlap))
    if np.count_nonzero(overlap) > 0:
        skull_new = skull_new & ~overlap
        print("overlap cleared; remaining:",
              np.count_nonzero(skull_new & csf_new))

    # ---- save updated masks ----
    skull_out_img = nib.Nifti1Image(skull_new.astype(np.uint8), skull_img.affine)
    csf_out_img   = nib.Nifti1Image(csf_new.astype(np.uint8), csf_img.affine)

    skull_out_path = os.path.join(OUT_DIR, subject_root + "_skull_without_interface.nii.gz")
    csf_out_path   = os.path.join(OUT_DIR, subject_root + "_CSF_with_interface.nii.gz")

    nib.save(skull_out_img, skull_out_path)
    nib.save(csf_out_img, csf_out_path)

    print("Saved:", skull_out_path)
    print("Saved:", csf_out_path)

def fill_brain_and_csf_separately(
    brain_mask_path: Path,
    csf_mask_path: Path,
    out_brain_path: Path,
    out_csf_path: Path,
    closing_radius: int = 1,
) -> None:
    brain_img = nib.load(str(brain_mask_path))
    csf_img = nib.load(str(csf_mask_path))

    brain = brain_img.get_fdata() > 0
    csf = csf_img.get_fdata() > 0

    if brain.shape != csf.shape:
        raise ValueError(f"Shape mismatch: brain {brain.shape}, CSF {csf.shape}")

    brain_csf = brain | csf

    selem = ball(closing_radius)
    closed = binary_closing(brain_csf, structure=selem) 
    filled = binary_fill_holes(closed)  

    # Voxels that were added by filling (not present in original brain+CSF)
    added = filled & ~brain_csf

    # Keep original masks inside filled support
    brain_filled = (brain & filled)
    csf_filled = (csf & filled)

    # Assign added voxels to CSF (you can change this rule if needed)
    csf_filled |= added

    brain_img_out = nib.Nifti1Image(
        brain_filled.astype(np.uint8), brain_img.affine, brain_img.header
    )
    csf_img_out = nib.Nifti1Image(
        csf_filled.astype(np.uint8), csf_img.affine, csf_img.header
    )

    nib.save(brain_img_out, str(out_brain_path))
    nib.save(csf_img_out, str(out_csf_path))