import os
import nibabel as nib
import numpy as np
from skimage.measure import label
from skimage.morphology import ball, binary_opening
import matplotlib.pyplot as plt

def extract_skull(segmented_input_file, original_t1_file, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)

    # Load MRI
    mri_img = nib.load(original_t1_file)
    mri_data = mri_img.get_fdata()

    # Load segmentation and create mask for label 0
    seg_img = nib.load(segmented_input_file)
    seg_data = seg_img.get_fdata().astype(int)

    skull_mask = (seg_data == 0)

    # Intensity threshold to keep only bone-like tissue
    bone_threshold = np.percentile(mri_data[skull_mask], 80)
    bone_mask = (mri_data > bone_threshold) & skull_mask

    # Largest connected component
    labels = label(bone_mask, connectivity=1)
    if labels.max() > 0:
        largest_label = np.argmax(np.bincount(labels.flat)[1:]) + 1
        skull_clean = (labels == largest_label)
    else:
        skull_clean = bone_mask

    skull_clean = binary_opening(skull_clean, ball(2))
    skull_clean = skull_clean.astype(np.uint8)

    # ----- build output names from *segmented* input filename -----
    base = os.path.basename(segmented_input_file)
    root, ext = os.path.splitext(base)      # -> (..., ".gz")
    root, _   = os.path.splitext(root)      # -> (..., ".nii")

    nii_name = root + "_skull_only_clean.nii.gz"
    png_name = root + "_skull_slice.png"

    nii_path = os.path.join(destination_folder, nii_name)
    png_path = os.path.join(destination_folder, png_name)

    # Save cleaned mask
    nib.save(nib.Nifti1Image(skull_clean, mri_img.affine), nii_path)

    # Visualization: middle slice
    slice_idx = skull_clean.shape[2] // 2
    plt.imshow(skull_clean[:, :, slice_idx])
    plt.axis('off')
    plt.savefig(png_path, bbox_inches='tight', pad_inches=0)
    plt.close()


directory = '/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Resampled_segmented_files'
destination_folder = '/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Extracted_Skull'
original_t1_dir = '/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Original_T1_Scans'

for filename in os.listdir(directory):
    if not filename.endswith(".nii.gz"):
        continue

    full_path_segmented = os.path.join(directory, filename)

    # filename e.g. U01_..._tMRIreg_T1_SynthSeg_resamp.nii.gz
    base = os.path.basename(filename)
    root, ext = os.path.splitext(base)      # -> (..._SynthSeg_resamp, ".gz")
    root, _   = os.path.splitext(root)      # -> (..._SynthSeg_resamp, ".nii")

    # Remove the SynthSeg_resamp suffix to get original T1 name
    original_root = root.replace("_SynthSeg_resamp", "")  # -> ..._tMRIreg_T1
    original_name = original_root + ".nii.gz"
    full_path_original = os.path.join(original_t1_dir, original_name)

    if not os.path.exists(full_path_original):
        print("Missing original T1 for:", filename)
        print("  Expected:", full_path_original)
        continue

    extract_skull(full_path_segmented, full_path_original, destination_folder)