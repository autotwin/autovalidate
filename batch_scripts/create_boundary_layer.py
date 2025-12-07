#!/usr/bin/env python3
import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import (
    binary_erosion,
    binary_dilation,
    generate_binary_structure,
)

# ---------------- paths ----------------
base = "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts"

skull_file = os.path.join(
    base,
    "Extracted_Skull",
    "U01_HJF_0001_01_tMRIreg_T1_SynthSeg_resamp_skull_only_clean.nii.gz"
)

csf_file = os.path.join(
    base,
    "Extracted_CSF",
    "U01_HJF_0001_01_tMRIreg_T1_SynthSeg_resamp_CSF_mask.nii.gz"
)

out_dir = os.path.join(base, "Debug_Skull_CSF_Interface_Move")
os.makedirs(out_dir, exist_ok=True)

thickness = 3  # desired interface thickness in voxels

# ---------------- load masks ----------------
skull_img = nib.load(skull_file)
csf_img   = nib.load(csf_file)

skull = skull_img.get_fdata().astype(bool)
csf   = csf_img.get_fdata().astype(bool)

print("skull shape:", skull.shape)
print("csf shape:",   csf.shape)

# ---------------- compute interface inside skull ----------------
conn = generate_binary_structure(3, 2)  # 26-connectivity

# skull boundary voxels = skull - eroded skull
skull_eroded   = binary_erosion(skull, structure=conn)
skull_boundary = skull & ~skull_eroded

# interface (1-voxel) = skull boundary touching CSF
csf_dilated = binary_dilation(csf, structure=conn)
interface_1voxel = skull_boundary & csf_dilated

print("interface (1-voxel) voxels:", np.count_nonzero(interface_1voxel))

# thicken interface
if thickness <= 1:
    interface_thick = interface_1voxel.copy()
else:
    interface_thick = binary_dilation(
        interface_1voxel,
        structure=conn,
        iterations=thickness - 1,
    )

# keep layer inside skull
interface_thick = interface_thick & skull

print(f"interface ({thickness}-voxel) voxels:",
      np.count_nonzero(interface_thick))

# ---------------- move layer: skull -> CSF ----------------
skull_new = skull & ~interface_thick     # remove from skull
csf_new   = csf | interface_thick        # add to CSF

# paranoid check: ensure no overlap
overlap = skull_new & csf_new
print("overlap voxels after move:", np.count_nonzero(overlap))
if np.count_nonzero(overlap) > 0:
    skull_new = skull_new & ~overlap
    print("overlap cleared; remaining overlap:",
          np.count_nonzero(skull_new & csf_new))

# ---------------- save updated masks ----------------
skull_out_img = nib.Nifti1Image(skull_new.astype(np.uint8), skull_img.affine)
csf_out_img   = nib.Nifti1Image(csf_new.astype(np.uint8),   csf_img.affine)

skull_out_path = os.path.join(
    out_dir,
    f"skull_without_interface_thick{thickness}.nii.gz"
)
csf_out_path = os.path.join(
    out_dir,
    f"csf_with_interface_thick{thickness}.nii.gz"
)

nib.save(skull_out_img, skull_out_path)
nib.save(csf_out_img,   csf_out_path)

print("Saved:", skull_out_path)
print("Saved:", csf_out_path)

# ---------------- visualize one slice: skull gray, CSF magenta ----------------
# choose a slice that has skull or CSF
combined = skull_new | csf_new
z_indices = np.where(combined.any(axis=(0, 1)))[0]
if z_indices.size == 0:
    raise RuntimeError("Combined mask empty in all slices")

z = int(z_indices[len(z_indices) // 2])
print("Using slice z =", z)

sl_skull = skull_new[:, :, z]
sl_csf   = csf_new[:, :, z]

h, w = sl_skull.shape
rgb = np.zeros((h, w, 3), dtype=float)

# skull = gray
rgb[sl_skull] = [0.5, 0.5, 0.5]
# CSF (including moved layer) = magenta
rgb[sl_csf] = [1.0, 0.0, 1.0]

plt.figure(figsize=(4, 4))
plt.imshow(rgb, origin="lower")
plt.axis("off")
plt.tight_layout()
png_out = os.path.join(
    out_dir,
    f"skull_gray_csf_magenta_thick{thickness}_z{z}.png"
)
plt.savefig(png_out, bbox_inches="tight", pad_inches=0)
plt.close()

print("Saved visualization:", png_out)
