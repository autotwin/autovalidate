#!/usr/bin/env python3
import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

from skimage.morphology import binary_closing, binary_opening, ball

# ---------------- paths and IDs ----------------
brains_dir  = "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Extracted_Brains"
strains_dir = "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Strains_Scans"
out_dir     = "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Debug_Brain_Strain_Overlap"

os.makedirs(out_dir, exist_ok=True)

subj_id    = "U01_HJF_0001_01"
mask_file  = os.path.join(
    brains_dir,
    f"{subj_id}_tMRIreg_T1_SynthSeg_resamp_brain_mask.nii.gz"
)
strain_file = os.path.join(
    strains_dir,
    "U01_HJF_0001_01_NR_HFE12_r5_E1_fit.nii.gz"
)

# ---------------- load images ----------------
mask_img   = nib.load(mask_file)
strain_img = nib.load(strain_file)

mask_data   = mask_img.get_fdata().astype(bool)   # (X,Y,Z)
strain_data = strain_img.get_fdata()              # (X,Y,Z,T)

print("mask shape:", mask_data.shape)
print("strain shape:", strain_data.shape)

# ---------------- choose a valid time frame (skip t=0) ----------------
T = strain_data.shape[3]
time_index = None
for t in range(1, T):
    vol_t = strain_data[..., t]
    if np.count_nonzero(np.isfinite(vol_t)) > 0:
        time_index = t
        break

if time_index is None:
    raise RuntimeError("No finite voxels in any time frame")

vol = strain_data[..., time_index]                # 3D strain volume
print("Using time_index:", time_index)

# ---------------- basic mask cleaning (optional) ----------------
# light closing/opening to remove tiny holes/specks only
mask_clean3d = binary_closing(mask_data, ball(1))
mask_clean3d = binary_opening(mask_clean3d, ball(1))

# ---------------- enforce overlap: mask AND finite strain ----------------
finite = np.isfinite(vol)
overlap_mask = mask_clean3d & finite             # only voxels with mask and valid strain

print("brain mask voxels:", np.count_nonzero(mask_clean3d))
print("finite strain voxels:", np.count_nonzero(finite))
print("overlap voxels:", np.count_nonzero(overlap_mask))

# ---------------- choose a z-slice that has overlap ----------------
z_indices = np.where(overlap_mask.any(axis=(0, 1)))[0]
if z_indices.size == 0:
    raise RuntimeError("Overlap mask empty in all slices")

z = int(z_indices[len(z_indices)//2])
print("Using slice z =", z)

slice_strain = vol[:, :, z]
slice_mask   = overlap_mask[:, :, z]

print("slice overlap voxels:", np.count_nonzero(slice_mask))

# ---------------- debug overlay: overlap contour on raw strain ----------------
plt.figure(figsize=(4, 4))
plt.imshow(slice_strain.T, cmap="gray", origin="lower")
plt.contour(slice_mask.T, levels=[0.5], colors="cyan", linewidths=0.5)
plt.axis("off")
plt.tight_layout()
plt.savefig(
    os.path.join(out_dir, f"{subj_id}_t{time_index}_debug_overlap_edges.png"),
    bbox_inches="tight", pad_inches=0
)
plt.close()

# ---------------- masked strain heatmap (only overlapping voxels) ----------------
slice_masked = np.where(slice_mask, slice_strain, 0)

print(
    "slice_masked min/max:",
    float(np.nanmin(slice_masked)),
    float(np.nanmax(slice_masked))
)

plt.figure(figsize=(4, 4))
im = plt.imshow(slice_masked.T, cmap="hot", origin="lower")
plt.axis("off")
cbar = plt.colorbar(im)
cbar.set_label("Strain")
plt.tight_layout()
plt.savefig(
    os.path.join(out_dir, f"{subj_id}_t{time_index}_brain_strain_overlap_masked.png"),
    bbox_inches="tight", pad_inches=0
)
plt.close()
