import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import collections
import os


def extract_CSF(input_file, destination_folder):
    
    # Create destination directory if needed
    os.makedirs(destination_folder, exist_ok=True)

    # Load SynthSeg segmentation
    seg_img = nib.load(input_file)
    seg = seg_img.get_fdata().astype(int)

    label_counts = collections.Counter(seg.flatten())

    csf_labels = [24]  # Add 49, 50 if you wish to include choroid plexus

    csf_mask = np.isin(seg, csf_labels).astype(np.uint8)

    # base name without directory
    base = os.path.basename(input_file) 
    
    root, ext = os.path.splitext(base)
    root, _   = os.path.splitext(root)

    mask_name = root + "_CSF_mask.nii.gz"
    png_name  = root + "_CSF_mask_slice.png"

    mask_path = os.path.join(destination_folder, mask_name)
    png_path  = os.path.join(destination_folder, png_name)

    nib.save(nib.Nifti1Image(csf_mask, seg_img.affine), mask_path)

    # Use the mask itself for visualization
    CSF_data = csf_mask
    sl = CSF_data.shape[2] // 2
    slice_data = CSF_data[:, :, sl]

    plt.imshow(slice_data, cmap='gray')
    plt.axis('off')
    plt.savefig(png_path, bbox_inches='tight', pad_inches=0)  # explicit path [web:104][web:111]
    plt.close()

directory = '/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Resampled_segmented_files'

destination_folder = '/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Extracted_CSF'

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".gz"): 
        full_path = os.path.join(directory, filename)
        extract_CSF(full_path, destination_folder)
    else:
        print("Not Such File")