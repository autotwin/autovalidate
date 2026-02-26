from pathlib import Path
from typing import List
import os
import subprocess
import nibabel as nib
import numpy as np


def find_t1_scans(root: Path, name_substring: str = "T1") -> List[Path]:
    """
    Return all .nii.gz files directly under `root`. If `root` is a file, 
    return just that file.
    """
    root = Path(root)
    
    if root.is_file():
        return [root]
 
    return sorted(
        p
        for p in root.iterdir()
        if p.is_file()
        and p.suffix == ".gz"
        and name_substring in p.name
        and p.name.endswith(".nii.gz")
    )


def _synthseg_output_path(input_path: Path, output_root: Path) -> Path:
    """
    Given an input T1 path, return the full output path for the corresponding
    SynthSeg segmentation under output_root, appending '_SynthSeg.nii.gz'.
    """
    input_path = Path(input_path)
    output_root = Path(output_root)

    name = input_path.name
    if name.endswith(".nii.gz"):
        stem = name[:-7]  # strip ".nii.gz"
    else:
        stem = input_path.stem

    out_name = stem + "_SynthSeg.nii.gz"
    return output_root / out_name



def _subject_id_from_t1(t1_path: Path) -> str:
    parts = t1_path.name.split("_")
    if len(parts) >= 4:
        return "_".join(parts[:4])          # e.g. U01_HJF_0001_01
    return t1_path.stem.split(".nii")[0]



def _find_strain_for_t1(t1_path: Path, strain_root: Path) -> Path | None:
    """
    Find a strain file in strain_root whose name starts with the same subject
    prefix as the T1.

    Example:
      T1:   U01_HJF_0001_01_tMRIreg_T1.nii.gz
      Strain candidates:
            U01_HJF_0001_01_NR_HFE12_r5_E1_fit.nii.gz
            U01_HJF_0001_01_NE_HFE42_r5_E1_fit.nii.gz
      We match on 'U01_HJF_0001_01'.
    """
    t1_path = Path(t1_path)
    strain_root = Path(strain_root)

    name = t1_path.name
    parts = name.split("_")
    if len(parts) >= 4:
        subj_prefix = "_".join(parts[:4])  # e.g. U01_HJF_0001_01
    else:
        subj_prefix = name.split(".nii")[0]

    candidates = sorted(strain_root.glob(f"{subj_prefix}*.nii.gz"))
    if not candidates:
        return None
    if len(candidates) > 1:
        print(f"[STRAIN] Multiple strain candidates for {t1_path}, using {candidates[0]}")
    return candidates[0]


def run_synthseg_and_resample_strain(
    *,
    t1_root: Path,
    strain_root: Path,
    synthseg_root: Path,
    resampled_strain_root: Path,
    mri_synthseg_path: Path,
    mri_convert_path: Path,
    extra_args: list[str] | None = None,
) -> None:
    """
    For each T1 in t1_root:
      1) Run mri_synthseg(T1) and write segmentation to synthseg_root.
      2) Find the matching 4D strain scan in strain_root.
      3) Extract the 2nd time frame (index 1).
      4) Run mri_convert to resample that 3D frame to the SynthSeg grid and
         write it to resampled_strain_root.
    """
    t1_root = Path(t1_root)
    strain_root = Path(strain_root)
    synthseg_root = Path(synthseg_root)
    resampled_strain_root = Path(resampled_strain_root)

    synthseg_root.mkdir(parents=True, exist_ok=True)
    resampled_strain_root.mkdir(parents=True, exist_ok=True)

    t1s = find_t1_scans(t1_root)
    if not t1s:
        print(f"No T1 scans found under {t1_root}")
        return

    print(f"Found {len(t1s)} T1 scans under {t1_root}")

    for t1 in t1s:
        # 1) SynthSeg labelmap
        seg_out = _synthseg_output_path(t1, synthseg_root)
        seg_out.parent.mkdir(parents=True, exist_ok=True)

        subject_id = _subject_id_from_t1(t1)

        seg_cmd = [
            str(mri_synthseg_path),
            "--i", str(t1),
            "--o", str(seg_out),
            *(extra_args or []),
        ]
        print("COMMAND:", " ".join(seg_cmd))
        seg_res = subprocess.run(
            seg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if seg_res.returncode != 0:
            print(f"[ERROR] SynthSeg failed for {t1}")
            print(seg_res.stderr)
            continue

        # 2) Find matching strain scan
        strain_path = _find_strain_for_t1(t1, strain_root)
        if strain_path is None or not strain_path.exists():
            print(f"[STRAIN] Missing strain for {t1} under {strain_root}")
            continue

        strain_img = nib.load(strain_path)
        strain_data = strain_img.get_fdata()
        if strain_data.ndim != 4 or strain_data.shape[3] < 2:
            print(f"[STRAIN] Unexpected shape for {strain_path}: {strain_data.shape}")
            continue

        frames = strain_data.shape[3]
        print(f"[INFO] Processing {frames} frames for subject {subject_id}")

        subj_dir = resampled_strain_root / subject_id
        subj_dir.mkdir(parents=True, exist_ok=True)

        for k in range(frames):

            k_frame = strain_data[..., k]

            # Save this 3D frame to a temporary NIfTI
            tmp_frame_path = subj_dir / f"{subject_id}_strain_frame{k}_tmp.nii.gz"
            nib.save(
                nib.Nifti1Image(k_frame.astype(np.float32), strain_img.affine, header=None),
                str(tmp_frame_path),
            )

            # 4) Resample this 3D frame to SynthSeg grid
            resamp_strain = subj_dir / f"{subject_id}_frame{k}_strain_resamp.nii.gz"
            resamp_strain.parent.mkdir(parents=True, exist_ok=True)

            conv_cmd = [
                str(mri_convert_path),
                "--resample_type", "interpolate",
                str(tmp_frame_path),
                "--like", str(seg_out),
                str(resamp_strain),
            ]
            print("COMMAND:", " ".join(conv_cmd))
            conv_res = subprocess.run(
                conv_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if conv_res.returncode != 0:
                print(f"[ERROR] mri_convert failed for {strain_path}")
                print(conv_res.stderr)
            else:
                print(f"[OK] Resampled strain (frame {k+1}) to {resamp_strain}")
                # Remove temporary 3D frame file to avoid clutter
                try:
                    os.remove(tmp_frame_path)
                except OSError as e:
                    print(f"[WARN] Could not delete temporary file {tmp_frame_path}: {e}")