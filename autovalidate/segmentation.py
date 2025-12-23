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


def extract_CSF(input_file, destination_folder):
    """
    If input_file is a directory, process all .nii/.nii.gz in it.
    If it is a file, process just that file.
    """
    destination_folder = Path(destination_folder)
    os.makedirs(destination_folder, exist_ok=True)

    for seg_path in _iter_nii_files(Path(input_file)):
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


def _remove_small_components(mask, min_size=5000, connectivity=1):
    """Keep only connected components with at least min_size voxels."""
    labels = label(mask, connectivity=connectivity)
    counts = np.bincount(labels.ravel())
    counts[0] = 0  # background
    keep = np.where(counts >= min_size)[0]
    cleaned = np.isin(labels, keep)
    return cleaned

def outer_shell_brain_csf(brain_mask_img, csf_mask_img,
                          thickness_vox=5,
                          min_cc_size=0):
    """
    Create an outer shell of fixed thickness around brain+CSF.
    """
    brain = brain_mask_img.get_fdata() > 0
    csf   = csf_mask_img.get_fdata() > 0
    brain_csf = brain | csf

    # 1) dilate brain+CSF
    struct = ball(thickness_vox)
    dil = binary_dilation(brain_csf, structure=struct)

    # 2) outer shell: dilated minus original
    shell = dil & (~brain_csf)

    # 3) optional small-component removal
    if min_cc_size > 0:
        shell = _remove_small_components(shell, min_size=min_cc_size)

    return shell.astype(np.uint8)


def process_subject(brain_mask_path, csf_mask_path, out_dir,
                    thickness_vox=5, min_cc_size=0):
    brain_img = nib.load(brain_mask_path)
    csf_img   = nib.load(csf_mask_path)

    if brain_img.shape != csf_img.shape:
        raise RuntimeError(f"Shape mismatch: {brain_mask_path} vs {csf_mask_path}")

    shell = outer_shell_brain_csf(
        brain_img, csf_img,
        thickness_vox=thickness_vox,
        min_cc_size=min_cc_size,
    )

    base = os.path.basename(brain_mask_path)
    root, _ = os.path.splitext(base)
    root, _ = os.path.splitext(root)
    subject_root = root.replace("_brain_mask", "")

    out_nii = os.path.join(out_dir, subject_root + "_braincsf_outer_shell.nii.gz")

    nib.save(nib.Nifti1Image(shell, brain_img.affine, brain_img.header), out_nii)

    print("Saved shell:", out_nii)


def process_all_brain_csf_shells(
    brain_dir: Path,
    csf_dir: Path,
    out_dir: Path,
    thickness_vox: int = 5,
    min_cc_size: int = 0,
) -> None:
    """
    For every brain mask in brain_dir, find the matching CSF mask in csf_dir
    and create the outer shell (skull-like) mask in out_dir. [file:112]
    """
    brain_dir = Path(brain_dir)
    csf_dir = Path(csf_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    brain_masks = sorted(brain_dir.glob("*_brain_mask.nii.gz"))

    for brain_mask_path in brain_masks:
        base = brain_mask_path.name  # e.g. U01_..._SynthSeg_resamp_brain_mask.nii.gz
        root, _ = os.path.splitext(base)
        root, _ = os.path.splitext(root)
        subject_root = root.replace("_brain_mask", "")

        csf_name = subject_root + "_CSF_mask.nii.gz"
        csf_mask_path = csf_dir / csf_name

        if not csf_mask_path.exists():
            print(f"[SKULL] Missing CSF mask for {brain_mask_path}, expected {csf_mask_path}")
            continue

        process_subject(
            str(brain_mask_path),
            str(csf_mask_path),
            str(out_dir),
            thickness_vox=thickness_vox,
            min_cc_size=min_cc_size,
        )