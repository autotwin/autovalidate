import os
import glob
import nibabel as nib
import numpy as np


def _find_strain_keyword(strain_dir, subj_root):
    """
    Search the Original_Strain_Scans directory for a file matching the subj_root.
    Returns 'NR', 'NE', or '' if neither is found.
    """
    # Assuming subject root is something like 'U01_HJF_0001_01'
    # We look for any file starting with this subject root
    search_pattern = os.path.join(strain_dir, f"{subj_root}*")
    matches = glob.glob(search_pattern)
    
    if not matches:
        return ""
        
    # Just check the first matching file
    filename = os.path.basename(matches[0])
    
    if "NR" in filename:
        return "NR"
    elif "NE" in filename:
        return "NE"
        
    return ""


def combine_all_components(BRAIN_DIR, CSF_DIR, SKULL_DIR, STRAIN_DIR, OUT_DIR, subj_root):
    brain_file = os.path.join(
        BRAIN_DIR,
        f"{subj_root}_brain_clean.nii.gz",
    )
    csf_file = os.path.join(
        CSF_DIR,
        f"{subj_root}_csf_clean.nii.gz",
    )
    skull_file = os.path.join(
        SKULL_DIR,
        f"{subj_root}_skull_clean.nii.gz",
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

    # ---------- Find NR / NE keyword ----------
    keyword = _find_strain_keyword(STRAIN_DIR, subj_root)
    keyword_str = f"_{keyword}" if keyword else ""

    print("\n=== Subject:", subj_root, "===")
    print(f"Detected keyword: '{keyword}'")
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
        f"{subj_root}{keyword_str}_tMRIreg_T1_SynthSeg_combined_labels.nii.gz",
    )
    nib.save(nib.Nifti1Image(labels, brain_img.affine, brain_img.header), out_nii)
    print("Saved combined labels NIfTI:", out_nii)

    # ---------- save combined NumPy array ----------
    out_npy = os.path.join(
        OUT_DIR,
        f"{subj_root}{keyword_str}_tMRIreg_T1_SynthSeg_combined_labels.npy",
    )
    np.save(out_npy, labels)
    print("Saved combined labels NumPy:", out_npy)

