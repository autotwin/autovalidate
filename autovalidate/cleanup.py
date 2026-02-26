import os
import nibabel as nib
import numpy as np

def fix_overlaps_for_subject(BRAIN_DIR, CSF_DIR, SKULL_DIR, OUT_DIR, subj_root):
    """
    subj_root example: U01_HJF_0001_01

    Expected files:
      brain: BRAIN_DIR / f"{subj_root}_tMRIreg_T1_SynthSeg_resamp_brain_mask.nii.gz"
      csf:   CSF_DIR   / f"{subj_root}_csf_with_interface_filled_only.nii.gz"
      skull: SKULL_DIR / f"{subj_root}_skull_without_interface_smallholes_filled.nii.gz"
    """
    brain_file = os.path.join(
        BRAIN_DIR,
        f"{subj_root}_tMRIreg_T1_SynthSeg_brain_mask.nii.gz",
    )
    csf_file = os.path.join(
        CSF_DIR,
        f"{subj_root}_tMRIreg_T1_SynthSeg_CSF_with_inner_layer.nii.gz",
    )
    skull_file = os.path.join(
        SKULL_DIR,
        f"{subj_root}_tMRIreg_T1_SynthSeg_skull_without_inner_layer.nii.gz",
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
    csf_img   = nib.load(csf_file)
    skull_img = nib.load(skull_file)

    brain = brain_img.get_fdata().astype(bool)
    csf   = csf_img.get_fdata().astype(bool)
    skull = skull_img.get_fdata().astype(bool)

    # ---------- resolve overlaps: brain > CSF > skull ----------
    skull_clean = skull.copy()
    csf_clean   = csf.copy()
    brain_clean = brain.copy()

    # brain wins over both CSF and skull
    csf_clean[brain_clean]   = False
    skull_clean[brain_clean] = False

    # CSF wins over skull
    skull_clean[csf_clean] = False

    print("after cleanup, skull U brain:",
          np.count_nonzero(skull_clean & brain_clean))
    print("after cleanup, skull U csf: ",
          np.count_nonzero(skull_clean & csf_clean))
    print("after cleanup, brain U csf: ",
          np.count_nonzero(brain_clean & csf_clean))

    # ---------- save cleaned separate NIfTIs ----------
    brain_out = os.path.join(OUT_DIR, f"{subj_root}_brain_clean.nii.gz")
    csf_out   = os.path.join(OUT_DIR, f"{subj_root}_csf_clean.nii.gz")
    skull_out = os.path.join(OUT_DIR, f"{subj_root}_skull_clean.nii.gz")

    nib.save(
        nib.Nifti1Image(brain_clean.astype(np.uint8),
                        brain_img.affine, brain_img.header),
        brain_out,
    )
    nib.save(
        nib.Nifti1Image(csf_clean.astype(np.uint8),
                        csf_img.affine, csf_img.header),
        csf_out,
    )
    nib.save(
        nib.Nifti1Image(skull_clean.astype(np.uint8),
                        skull_img.affine, skull_img.header),
        skull_out,
    )

    print("Saved cleaned brain:", brain_out)
    print("Saved cleaned CSF:", csf_out)
    print("Saved cleaned skull:", skull_out)
