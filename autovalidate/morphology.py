import os
from pathlib import Path
import nibabel as nib
import numpy as np
from scipy.ndimage import binary_dilation
from skimage.morphology import ball

def add_inner_skull_to_csf(
    skull_mask: np.ndarray,
    csf_mask: np.ndarray,
    inner_thickness_voxels: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Take a skull shell mask and CSF mask, extract a thin inner skull layer
    adjacent to CSF, and add that layer into the CSF mask.

    Inner layer is defined as skull voxels that lie within a dilated CSF
    neighborhood of user-defined voxel thickness.

    Parameters
    ----------
    skull_mask : np.ndarray
        Binary skull shell mask (0/1).
    csf_mask : np.ndarray
        Binary CSF mask (0/1), same shape as skull_mask.
    inner_thickness_voxels : int
        Thickness (in voxels) of the CSF neighborhood used to pick inner layer.

    Returns
    -------
    new_csf : np.ndarray
        CSF mask including the inner skull layer.
    new_skull : np.ndarray
        Skull mask with that inner layer removed.
    """
    if skull_mask.shape != csf_mask.shape:
        raise ValueError("skull_mask and csf_mask must have the same shape")
    if inner_thickness_voxels <= 0:
        raise ValueError("inner_thickness_voxels must be > 0")

    print(f"   -> Dilating CSF by {inner_thickness_voxels} voxels to identify boundary layer...")
    skull = skull_mask.astype(bool)
    csf = csf_mask.astype(bool)

    # 1) Dilate CSF outwards by the requested thickness
    struct = ball(inner_thickness_voxels)  # 3D neighborhood 
    csf_dil = binary_dilation(csf, structure=struct)  # CSF neighborhood 

    # 2) Inner skull layer = skull voxels that lie inside the dilated CSF region
    print("   -> Transferring intersecting voxels from Skull to CSF...")
    inner_layer = skull & csf_dil

    # 3) New masks
    new_csf = csf | inner_layer          # move inner layer into CSF
    new_skull = skull & ~inner_layer     # remove it from skull

    transferred = np.count_nonzero(inner_layer)
    print(f"   -> Successfully transferred {transferred} voxels.")

    return new_csf.astype(np.uint8), new_skull.astype(np.uint8)


def process_one_subject(
    brain_dir: str | Path,
    csf_dir: str | Path,
    skull_dir: str | Path,
    out_dir: str | Path,
    subject_root: str,
    inner_thickness_voxels: int = 2,
) -> None:
    """
    For one subject:
      - Load CSF and skull masks.
      - Extract an inner skull layer adjacent to CSF (user-defined thickness).
      - Add that layer to CSF and remove it from skull.
      - Save NEW CSF and NEW skull masks as separate files.
    """
    brain_dir = Path(brain_dir)
    csf_dir = Path(csf_dir)
    skull_dir = Path(skull_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[BOUNDARY] Processing morphology for subject: {subject_root}")

    csf_path = csf_dir / f"{subject_root}_CSF_mask.nii.gz"
    skull_path = skull_dir / f"{subject_root}_skull_mask.nii.gz"

    if not csf_path.exists():
        print(f"[ERROR] CSF mask not found: {csf_path}")
        raise FileNotFoundError(f"CSF mask not found: {csf_path}")
    if not skull_path.exists():
        print(f"[ERROR] Skull mask not found: {skull_path}")
        raise FileNotFoundError(f"Skull mask not found: {skull_path}")

    print("   -> Loading original CSF and Skull masks...")
    csf_img = nib.load(str(csf_path))
    skull_img = nib.load(str(skull_path))

    csf_mask = csf_img.get_fdata().astype(np.uint8)
    skull_mask = skull_img.get_fdata().astype(np.uint8)

    new_csf, new_skull = add_inner_skull_to_csf(
        skull_mask=skull_mask,
        csf_mask=csf_mask,
        inner_thickness_voxels=inner_thickness_voxels,
    )

    print("   -> Saving updated NIfTI files...")
    # Save NEW CSF mask
    new_csf_path = out_dir / f"{subject_root}_CSF_with_inner_layer.nii.gz"
    new_csf_img = nib.Nifti1Image(new_csf.astype(np.uint8), csf_img.affine, csf_img.header)
    nib.save(new_csf_img, str(new_csf_path))
    print(f"      - {new_csf_path.name}")

    # Save NEW skull mask
    new_skull_path = out_dir / f"{subject_root}_skull_without_inner_layer.nii.gz"
    new_skull_img = nib.Nifti1Image(new_skull.astype(np.uint8), skull_img.affine, skull_img.header)
    nib.save(new_skull_img, str(new_skull_path))
    print(f"      - {new_skull_path.name}")
