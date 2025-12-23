import os

import nibabel as nib
import numpy as np


def combine_all_components(BRAIN_DIR, CSF_DIR, SKULL_DIR, OUT_DIR, subj_root):
    brain_file = os.path.join(
        BRAIN_DIR,
        f"{subj_root}_tMRIreg_T1_SynthSeg_brain_mask.nii.gz",
    )
    csf_file = os.path.join(
        CSF_DIR,
        f"{subj_root}_tMRIreg_T1_SynthSeg_CSF_with_interface.nii.gz",
    )
    skull_file = os.path.join(
        SKULL_DIR,
        f"{subj_root}_tMRIreg_T1_SynthSeg_skull_without_interface.nii.gz",
    )

    if not os.path.exists(brain_file):
        print("Missing brain:", brain_file)
        return
    if not os.path.exists(csf_file):
        print("Missing CSF:", csf_file)
        return
    if not os.path.exists(skull_file):
        print("Missing skull:", skull_file)
        return

    print("\n=== Subject:", subj_root, "===")
    print("brain:", brain_file)
    print("csf:", csf_file)
    print("skull:", skull_file)

    # ---------- load masks ----------
    brain_img = nib.load(brain_file)
    csf_img = nib.load(csf_file)
    skull_img = nib.load(skull_file)

    brain = brain_img.get_fdata().astype(bool)
    csf = csf_img.get_fdata().astype(bool)
    skull = skull_img.get_fdata().astype(bool)

    # 0 = background, 1 = brain, 2 = CSF, 3 = skull
    labels = np.zeros(brain.shape, dtype=np.uint8)
    labels[brain] = 1
    labels[csf] = 2
    labels[skull] = 3

    # ---------- save combined NIfTI ----------
    out_nii = os.path.join(
        OUT_DIR,
        f"{subj_root}_tMRIreg_T1_SynthSeg_combined_labels.nii.gz",
    )
    nib.save(nib.Nifti1Image(labels, brain_img.affine, brain_img.header), out_nii)
    print("Saved combined labels NIfTI:", out_nii)

    # ---------- save combined NumPy array ----------
    out_npy = os.path.join(
        OUT_DIR,
        f"{subj_root}_tMRIreg_T1_SynthSeg_combined_labels.npy",
    )
    np.save(out_npy, labels)
    print("Saved combined labels NumPy:", out_npy)
