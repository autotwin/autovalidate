#!/usr/bin/env python3
import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

brains_dir  = "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Extracted_Brains"
strains_dir = "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Strains_Scans"
out_dir     = "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Brain_Strain_Heatmaps"

os.makedirs(out_dir, exist_ok=True)

strain_files = os.listdir(strains_dir)

def find_strain_for_subject(subj_id):
    """Return full path to strain file whose name starts with subj_id."""
    cands = [f for f in strain_files if f.startswith(subj_id) and f.endswith(".nii.gz")]
    if len(cands) == 0:
        print("No strain file for", subj_id)
        return None
    if len(cands) > 1:
        print("Multiple strain files for", subj_id, ":", cands)
        return None
    return os.path.join(strains_dir, cands[0])

def plot_brain_strain_heatmap(mask_file, strain_file):
    # ----- load mask -----
    mask_img = nib.load(mask_file)
    mask = mask_img.get_fdata().astype(bool)          # 3D

    # ----- load strain -----
    strain_img = nib.load(strain_file)
    data = strain_img.get_fdata()                     # 4D (X,Y,Z,T)
    T = data.shape[3]

    # choose a good time frame (skip t=0 which is all-NaN)
    time_index = None
    for t in range(1, T):
        vol_t = data[..., t]
        finite = np.count_nonzero(np.isfinite(vol_t))
        if finite > 0:
            time_index = t
            break
    if time_index is None:
        print("All time frames are NaN in", strain_file)
        return

    vol = data[..., time_index]                       # 3D strain volume

    # ----- choose a slice where mask has voxels -----
    z_indices = np.where(mask.any(axis=(0, 1)))[0]
    if z_indices.size == 0:
        print("Mask empty for", mask_file)
        return
    z = int(z_indices[len(z_indices)//2])             # middle non-empty slice

    slice_strain = vol[:, :, z]
    slice_mask   = mask[:, :, z]

    # keep strain inside brain, zero outside
    slice_data = np.where(slice_mask, slice_strain, 0)

    # sanity print
    print(os.path.basename(mask_file),
          "time", time_index,
          "z", z,
          "min/max", float(np.nanmin(slice_data)), float(np.nanmax(slice_data)))

    # ----- plot -----
    plt.figure(figsize=(4, 4))
    im = plt.imshow(slice_data.T, cmap="hot", origin="lower")
    plt.axis("off")
    cbar = plt.colorbar(im)
    cbar.set_label("Strain")
    plt.tight_layout()

    base = os.path.basename(mask_file)
    subj_id = base.split("_tMRIreg_T1_")[0]
    out_png = os.path.join(out_dir, f"{subj_id}_t{time_index}_brain_strain_heatmap.png")
    plt.savefig(out_png, bbox_inches="tight", pad_inches=0)
    plt.close()

# ---------------- main loop over subjects ----------------

for fname in os.listdir(brains_dir):
    if not fname.endswith(".nii.gz"):
        continue
    if not fname.startswith("U01_"):
        # skip non-subject masks such as global brain_parenchyma_mask
        continue

    # from e.g. U01_HJF_0001_01_tMRIreg_T1_SynthSeg_resamp_brain_mask.nii.gz
    subj_id = fname.split("_tMRIreg_T1_")[0]
    mask_file = os.path.join(brains_dir, fname)

    strain_file = find_strain_for_subject(subj_id)
    if strain_file is None:
        continue

    plot_brain_strain_heatmap(mask_file, strain_file)


