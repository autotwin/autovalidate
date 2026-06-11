from autovalidate.io import file_io, filename_builder, nifti_io, npy_io, path_resolver
from autovalidate.cleanup import overlaps
from autovalidate.combine import combine_labels
from autovalidate.morphology import skull
from autovalidate.segmentation import common, fsl, slant, synthseg
from autovalidate import config

import argparse
import tomllib
from pathlib import Path
import subprocess
import tempfile

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    # Step 1: Load the TOML file
    print("[1/10] Loading config...")
    with open(args.config, "rb") as f:
        raw = tomllib.load(f)

    # Step 2: Parse the config
    cfg = config.parse_config(raw)
    print(f"       subject={cfg.subject_id}  algorithm={cfg.algorithm}  fidelity={cfg.brain_fidelity}  membranes={cfg.include_membranes}")

    # Step 3: Validate tool paths
    print("[2/10] Validating tool paths...")
    tools_to_check = {}
    if cfg.algorithm == "synthseg":
        tools_to_check["mri_synthseg"] = cfg.mri_synthseg
    elif cfg.algorithm == "fsl":
        tools_to_check["bet"]  = cfg.bet
        tools_to_check["fast"] = cfg.fast
    if cfg.include_membranes:
        tools_to_check["mri_convert"] = cfg.mri_convert
    for name, path in tools_to_check.items():
        if not Path(path).exists():
            raise FileNotFoundError(f"{name} binary not found at '{path}' — check your [env] config")
    print("       all tool paths OK")

    # Step 4: Resolve paths
    print("[3/10] Resolving input paths...")
    subj_dir = Path(cfg.subject_dir)
    algorithm = cfg.algorithm
    include_membranes = cfg.include_membranes

    path_dict = path_resolver.path_resolving(subj_dir, algorithm, include_membranes)

    # Step 5: Algorithm dispatch
    print(f"[4/10] Running segmentation ({algorithm})...")
    if algorithm == "synthseg":
        mri_synthseg_path = Path(cfg.mri_synthseg)
        T1_image_path = Path(path_dict["t1"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            synthseg_command_line = synthseg.create_synthseg_command(mri_synthseg_path, T1_image_path, Path(tmp_dir))
            subprocess.run(synthseg_command_line, check=True)
            seg_out_filepath = Path(tmp_dir) / (Path(T1_image_path.stem).stem + "_SynthSeg.nii.gz")
            seg_output_file_data, seg_output_file_affine = nifti_io.load_nifti(seg_out_filepath)

    elif algorithm == "fsl":
        bet_path  = Path(cfg.bet)
        fast_path = Path(cfg.fast)
        t1_path   = Path(path_dict["t1"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 1. BET: skull-strip the T1
            brain_prefix = Path(tmp_dir) / "brain"
            bet_command_line = fsl.create_bet_command(bet_path, t1_path, brain_prefix)
            subprocess.run(bet_command_line, check=True)
            # 2. FAST: tissue segmentation on brain-extracted image
            brain_path   = Path(tmp_dir) / "brain.nii.gz"
            fast_prefix  = Path(tmp_dir) / "fast"
            fast_command_line = fsl.create_fast_command(fast_path, brain_path, fast_prefix)
            subprocess.run(fast_command_line, check=True)
            # 3. Load hard segmentation (fast_seg.nii.gz)
            seg_out_filepath = Path(tmp_dir) / "fast_seg.nii.gz"
            seg_output_file_data, seg_output_file_affine = nifti_io.load_nifti(seg_out_filepath)

    elif algorithm == "slant":
        segmented_filepath = Path(path_dict["slant_seg"])
        seg_output_file_data, seg_output_file_affine = nifti_io.load_nifti(segmented_filepath)

    else:
        raise ValueError(f"Unknown algoritm: {algorithm}")

    # Step 6: Extract Masks
    print("[5/10] Extracting masks...")
    if algorithm == "synthseg":
        brain_mask = common.extract_mask(seg_output_file_data, synthseg.SYNTHSEG_BRAIN_EXCLUDE_LABELS, True)
        csf_mask = common.extract_mask(seg_output_file_data, synthseg.SYNTHSEG_CSF_LABELS, False)
        wm_mask = common.extract_mask(seg_output_file_data, synthseg.SYNTHSEG_WM_LABELS, False)
        gm_mask = common.extract_mask(seg_output_file_data, synthseg.SYNTHSEG_GM_LABELS, False)

    elif algorithm == "fsl":
        brain_mask = common.extract_mask(seg_output_file_data, fsl.FSL_BRAIN_EXCLUDE_LABELS, True)
        csf_mask   = common.extract_mask(seg_output_file_data, fsl.FSL_CSF_LABELS, False)
        wm_mask    = common.extract_mask(seg_output_file_data, fsl.FSL_WM_LABELS, False)
        gm_mask    = common.extract_mask(seg_output_file_data, fsl.FSL_GM_LABELS, False)

    elif algorithm == "slant":
        brain_mask = common.extract_mask(seg_output_file_data, slant.SLANT_BRAIN_EXCLUDE_LABELS, True)
        csf_mask = common.extract_mask(seg_output_file_data, slant.SLANT_CSF_LABELS, False)
        wm_mask = common.extract_mask(seg_output_file_data, slant.SLANT_WM_LABELS, False)
        gm_mask = common.extract_mask(seg_output_file_data, slant.SLANT_GM_LABELS, False)

    else:
        raise ValueError(f"Unknown algoritm: {algorithm}")


    # Step 7: Skull Pipeline
    print("[6/10] Building skull...")
    skull_mask = skull.create_skull(brain_mask, csf_mask)
    csf_mask, skull_mask = skull.ensure_no_brain_skull_contact(brain_mask, skull_mask, csf_mask)
    skull_mask = skull.remove_small_components(skull_mask, 10000)

    # Step 8: Resolve Overlaps
    print("[7/10] Resolving overlaps...")
    wm_mask, gm_mask, csf_mask, skull_mask = overlaps.resolve_overlaps(wm_mask, gm_mask, csf_mask, skull_mask)

    # Step 9: Include membranes and resolve overlaps
    print("[8/10] Processing membranes...")
    if include_membranes:
        falx_filepath = Path(path_dict["falx"])
        tentorium_filepath = Path(path_dict["tentorium"])
        mri_convert_path = Path(cfg.mri_convert)
        with tempfile.TemporaryDirectory() as tmp_dir:
            brain_mask_output_file = Path(tmp_dir) / "brain_mask_ref.nii.gz"
            nifti_io.save_nifti(brain_mask, seg_output_file_affine, brain_mask_output_file)
            falx_output_file = Path(tmp_dir) / "falx_resampled.nii.gz"
            falx_convert_command_line = file_io.create_mri_convert_command(mri_convert_path, falx_filepath, falx_output_file, brain_mask_output_file, "nearest")
            subprocess.run(falx_convert_command_line, check=True)
            tentorium_output_file = Path(tmp_dir) / "tentorium_resampled.nii.gz"
            tentorium_convert_command_line = file_io.create_mri_convert_command(mri_convert_path, tentorium_filepath, tentorium_output_file, brain_mask_output_file, "nearest")
            subprocess.run(tentorium_convert_command_line, check=True)
            falx_data, falx_affine = nifti_io.load_nifti(Path(tmp_dir) / "falx_resampled.nii.gz")
            tentorium_data, tentorium_affine = nifti_io.load_nifti(Path(tmp_dir) / "tentorium_resampled.nii.gz")
            membranes_mask = falx_data | tentorium_data
            membranes_mask, wm_mask, gm_mask, csf_mask, skull_mask = overlaps.resolve_membrane_priority(membranes_mask, wm_mask, gm_mask, csf_mask, skull_mask)
    else:
        print("       skipped (include_membranes = false)")
        membranes_mask = None

    # Step 10: Combine labels
    print(f"[9/10] Combining labels ({cfg.brain_fidelity})...")
    if cfg.brain_fidelity == "homogeneous":
        combined_labels = combine_labels.combine_labels_homogeneous(brain_mask, csf_mask, skull_mask, membranes_mask)

    elif cfg.brain_fidelity == "heterogeneous":
        combined_labels = combine_labels.combine_labels_heterogeneous(wm_mask, gm_mask, csf_mask, skull_mask, membranes_mask)

    else:
        raise ValueError(f"Unknown brain fidelity level: {cfg.brain_fidelity}")

    # Step 11: Save output
    print("[10/10] Saving outputs...")
    combined_npy_filename = filename_builder.filename_building(cfg.subject_id, cfg.motion_type, algorithm, cfg.brain_fidelity, include_membranes, "combined")
    npy_io.save_npy(combined_labels, file_path = Path(cfg.output_dir) / combined_npy_filename)

    print("        Saving .nii.gz...")
    combined_nii_filename = filename_builder.filename_building(cfg.subject_id, cfg.motion_type, algorithm, cfg.brain_fidelity, include_membranes, "combined")
    nifti_io.save_nifti(combined_labels, seg_output_file_affine, file_path = Path(cfg.output_dir) / combined_nii_filename)

    print(f"\nDone. Output files:")
    print(f"  {Path(cfg.output_dir) / combined_npy_filename}")
    print(f"  {Path(cfg.output_dir) / combined_nii_filename}")