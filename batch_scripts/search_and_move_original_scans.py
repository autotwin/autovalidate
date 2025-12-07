import os
import shutil

def move_files_by_keyword(src_root, dst_root, keywords, dry_run=True):
    """
    Search src_root (recursively) for files whose names contain any of the
    given keywords (case-insensitive) and move them to dst_root.

    src_root: folder to search
    dst_root: folder to move matching files into
    keywords: list of substrings to look for in filenames
    dry_run: if True, just print what would be moved
    """
    # Normalize keywords once
    keywords = [k.lower() for k in keywords]

    # Create destination directory if needed
    os.makedirs(dst_root, exist_ok=True)

    for root, dirs, files in os.walk(src_root):
        for fname in files:
            lower_name = fname.lower()
            if any(k in lower_name for k in keywords):
                src_path = os.path.join(root, fname)
                dst_path = os.path.join(dst_root, fname)

                # If the destination file exists, avoid overwriting
                if os.path.exists(dst_path):
                    base, ext = os.path.splitext(fname)
                    i = 1
                    while True:
                        new_name = f"{base}_{i}{ext}"
                        dst_path = os.path.join(dst_root, new_name)
                        if not os.path.exists(dst_path):
                            break
                        i += 1

                if dry_run:
                    print(f"[DRY RUN] Would move: {src_path} -> {dst_path}")
                else:
                    print(f"Moving: {src_path} -> {dst_path}")
                    shutil.copy(src_path, dst_path)  # high-level move function [web:7][web:18]

if __name__ == "__main__":
    source_folder = "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/NITRC_Dataset"
    destination_folder_original_scans = "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Original_T1_Scans"
    destination_folder_strains_scans = "/projectnb/lejlab2/Evangelos_Practice/FreeSurfer/batch_scripts/Strains_Scans"
    # Files whose names contain any of these substrings will be moved
    keyword_original_scans = ["tMRIreg_T1.nii.gz"]
    keyword_strains_scans = ["r5_E1_fit.nii.gz"]

    move_files_by_keyword(source_folder, destination_folder_original_scans, keyword_original_scans, dry_run=False)
    move_files_by_keyword(source_folder, destination_folder_strains_scans, keyword_strains_scans, dry_run=False)
    # After checking output, run again with dry_run=False to actually move
