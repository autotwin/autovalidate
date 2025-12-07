import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import os

def extract_brain(input_file, destination_folder):
    
    # Create destination directory if needed
    os.makedirs(destination_folder, exist_ok=True)

    seg_img = nib.load(input_file)
    seg_data = seg_img.get_fdata().astype(int)

    exclude_labels = [0, 4, 5, 14, 15, 24, 43, 44]  # background, all ventricles, CSF
    brain_mask = ~np.isin(seg_data, exclude_labels)  # True for brain parenchyma
    brain_mask = brain_mask.astype(np.uint8)

    # base name without directory
    base = os.path.basename(input_file)  # e.g. U01_..._SynthSeg_resamp.nii.gz [web:84]
    # strip full extension .nii.gz (do it twice)
    root, ext = os.path.splitext(base)   # -> (U01_..._SynthSeg_resamp.nii, .gz) [web:82][web:85]
    root, _   = os.path.splitext(root)   # -> (U01_..._SynthSeg_resamp, .nii)

    mask_name = root + "_brain_mask.nii.gz"
    png_name  = root + "_brain_mask_slice.png"

    mask_path = os.path.join(destination_folder, mask_name)
    png_path  = os.path.join(destination_folder, png_name)
    nib.save(nib.Nifti1Image(brain_mask, seg_img.affine), mask_path)

    # Use the mask itself for visualization
    brain_data = brain_mask
    sl = brain_data.shape[2] // 2
    slice_data = brain_data[:, :, sl]

    plt.imshow(slice_data, cmap='gray')
    plt.axis('off')
    plt.savefig(png_path, bbox_inches='tight', pad_inches=0)
    plt.close()


directory = '/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Resampled_segmented_files'

destination_folder = '/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Extracted_Brains'

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".gz"): 
        full_path = os.path.join(directory, filename)
        extract_brain(full_path, destination_folder)
    else:
        print("Not Such File")
