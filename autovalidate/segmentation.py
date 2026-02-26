import nibabel as nib
import numpy as np
import os
import collections
from pathlib import Path
from scipy.ndimage import binary_dilation
from skimage.measure import label
from skimage.morphology import ball, binary_opening


def _iter_nii_files(root: Path):
    root = Path(root)
    if root.is_file():
        if root.suffix in {".nii", ".gz"}:
            yield root
        return
    if root.is_dir():
        for p in sorted(root.iterdir()):
            if p.is_file() and (str(p).endswith("resamp.nii") or str(p).endswith("resamp.nii.gz")):
                yield p


def extract_brain(input_file, destination_folder):
    """
    If input_file is a directory, process all .nii/.nii.gz in it.
    If it is a file, process just that file.
    """
    destination_folder = Path(destination_folder)
    os.makedirs(destination_folder, exist_ok=True)

    for seg_path in _iter_nii_files(Path(input_file)):
        print(f"[BRAIN] Extracting brain mask from: {seg_path.name}")
        seg_img = nib.load(str(seg_path))
        seg_data = seg_img.get_fdata().astype(int)

        exclude_labels = [0, 24]  # background, CSF
        brain_mask = ~np.isin(seg_data, exclude_labels)
        brain_mask = brain_mask.astype(np.uint8)

        base = os.path.basename(str(seg_path))  # e.g. U01_..._SynthSeg_resamp.nii.gz
        root, ext = os.path.splitext(base)
        root, _ = os.path.splitext(root)
        mask_name = root + "_brain_mask.nii.gz"

        mask_path = destination_folder / mask_name
        nib.save(nib.Nifti1Image(brain_mask, seg_img.affine), str(mask_path))
        print(f"   -> Saved: {mask_path.name}")


def extract_CSF(input_file, destination_folder):
    """
    If input_file is a directory, process all .nii/.nii.gz in it.
    If it is a file, process just that file.
    """
    destination_folder = Path(destination_folder)
    os.makedirs(destination_folder, exist_ok=True)

    for seg_path in _iter_nii_files(Path(input_file)):
        print(f"[CSF] Extracting CSF mask from: {seg_path.name}")
        seg_img = nib.load(str(seg_path))
        seg = seg_img.get_fdata().astype(int)

        # label_counts could be used later; kept to match existing behavior
        _ = collections.Counter(seg.flatten())

        csf_labels = [24]
        csf_mask = np.isin(seg, csf_labels).astype(np.uint8)

        base = os.path.basename(str(seg_path))
        root, ext = os.path.splitext(base)
        root, _ = os.path.splitext(root)
        mask_name = root + "_CSF_mask.nii.gz"

        mask_path = destination_folder / mask_name
        nib.save(nib.Nifti1Image(csf_mask, seg_img.affine), str(mask_path))
        print(f"   -> Saved: {mask_path.name}")


def _remove_small_components(mask, min_size=5000, connectivity=1):
    """Keep only connected components with at least min_size voxels."""
    labels = label(mask, connectivity=connectivity)
    counts = np.bincount(labels.ravel())
    counts[0] = 0  # background
    keep = np.where(counts >= min_size)[0]
    cleaned = np.isin(labels, keep)
    return cleaned

def create_skull(brain_mask: np.ndarray, csf_mask: np.ndarray,
                 thickness_voxels: int,
                 min_size: int = 5000) -> np.ndarray:
    """
    Create a skull mask as an outward shell around the combined brain+CSF mask,
    and remove small connected-component islands.
    """
    if brain_mask.shape != csf_mask.shape:
        raise ValueError("brain_mask and csf_mask must have the same shape")
    if thickness_voxels <= 0:
        raise ValueError("thickness_voxels must be > 0")

    print(f"   -> Dilating combined mask by {thickness_voxels} voxels to create skull layer...")
    combined = (brain_mask.astype(bool) | csf_mask.astype(bool))

    struct = ball(thickness_voxels)
    outer = binary_dilation(combined, structure=struct)

    skull = outer & ~combined

    print(f"   -> Cleaning small disconnected components (min_size={min_size})...")
    # Remove small islands
    skull_clean = _remove_small_components(skull, min_size=min_size)

    return skull_clean.astype(np.uint8)


def process_all_brain_csf_skulls(
    synthseg_root: str | Path,
    brain_out: str | Path,
    csf_out: str | Path,
    skull_out: str | Path,
    thickness_voxels: int = 5,
    min_cc_size: int = 10000,
) -> None:
    """
    High-level pipeline:
      1) For each SynthSeg segmentation, save brain and CSF masks.
      2) Build skull (outer shell) masks from brain+CSF.
    """
    synthseg_root = Path(synthseg_root)
    brain_out = Path(brain_out)
    csf_out = Path(csf_out)
    skull_out = Path(skull_out)

    brain_out.mkdir(parents=True, exist_ok=True)
    csf_out.mkdir(parents=True, exist_ok=True)
    skull_out.mkdir(parents=True, exist_ok=True)

    print(f"=== Starting Step 1: Brain & CSF Extraction ===")
    # 1) Per segmentation: extract brain and CSF masks
    for file in os.listdir(synthseg_root):
        filename = os.fsdecode(file)
        if not filename.endswith(".gz"):
            continue

        full_path = synthseg_root / filename
        extract_brain(full_path, brain_out)
        extract_CSF(full_path, csf_out)

    print(f"\n=== Starting Step 2: Skull Shell Generation ===")
    # 2) Build skull masks
    for file in os.listdir(brain_out):
        filename = os.fsdecode(file)
        if not filename.endswith("_brain_mask.nii.gz"):
            continue

        base = filename.replace("_brain_mask.nii.gz", "")
        print(f"[SKULL] Processing subject: {base}")
        
        # Derive CSF mask path from brain mask filename
        brain_path = brain_out / filename
        csf_filename = base + "_CSF_mask.nii.gz"
        csf_path = csf_out / csf_filename

        if not csf_path.exists():
            print(f"[ERROR] CSF mask not found for {brain_path}: {csf_path}")
            raise FileNotFoundError(f"CSF mask not found for {brain_path}: {csf_path}")

        # Load masks
        brain_img = nib.load(str(brain_path))
        csf_img = nib.load(str(csf_path))

        brain_mask = brain_img.get_fdata().astype(np.uint8)
        csf_mask = csf_img.get_fdata().astype(np.uint8)

        # Create skull shell (with island removal)
        skull_mask = create_skull(
            brain_mask,
            csf_mask,
            thickness_voxels=thickness_voxels,
            # hook into _remove_small_components via min_size
            min_size=min_cc_size,
        )

        # Save skull mask
        skull_filename = base + "_skull_mask.nii.gz"
        skull_path = skull_out / skull_filename

        skull_img = nib.Nifti1Image(skull_mask.astype(np.uint8), brain_img.affine, brain_img.header)
        nib.save(skull_img, str(skull_path))
        print(f"   -> Saved: {skull_filename}\n")

    print("=== Processing Complete ===")
