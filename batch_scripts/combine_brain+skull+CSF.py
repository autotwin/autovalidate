import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# load boolean masks (3D)
brain = nib.load("/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Extracted_Brains/U01_HJF_0001_01_tMRIreg_T1_SynthSeg_resamp_brain_mask.nii.gz").get_fdata().astype(bool)
csf   = nib.load("/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Extracted_CSF/U01_HJF_0001_01_tMRIreg_T1_SynthSeg_resamp_CSF_mask.nii.gz").get_fdata().astype(bool)
skull = nib.load("/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Extracted_Skull/U01_HJF_0001_01_tMRIreg_T1_SynthSeg_resamp_skull_only_clean.nii.gz").get_fdata().astype(bool)

# 0 = background, 1 = brain, 2 = CSF, 3 = skull
labels = np.zeros(brain.shape, dtype=np.uint8)
labels[brain] = 1
labels[csf]   = 2
labels[skull] = 3

# choose slice index
z = labels.shape[2] // 2
lab_sl = labels[:, :, z]

# custom colormap: index -> color
# 0: background = black, 1: brain = yellow, 2: CSF = blue, 3: skull = magenta
cmap = ListedColormap([
    (0, 0, 0),        # 0 background
    (1, 1, 0),        # 1 brain: yellow
    (0, 0, 1),        # 2 CSF: blue
    (1, 0, 1),        # 3 skull: magenta
])

plt.figure(figsize=(4, 4))
plt.imshow(lab_sl.T, cmap=cmap, origin="lower", vmin=0, vmax=3)
plt.axis("off")
plt.tight_layout()
plt.savefig("brain_csf_skull_labels_z{}.png".format(z),
            bbox_inches="tight", pad_inches=0)
plt.close()
