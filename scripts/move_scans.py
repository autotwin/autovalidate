from autovalidate.io import move_files_by_keyword
import os

def main():

    # ===================== USER CONFIGURATION =====================
    # Edit these variables for your environment before running.

    # Directory where original T1 Scans are
    source_folder = "path/to/dataset"
    
    # Directory of your study
    BASE = "path/to/your/study"

    # Target directory for T1 Scans to be moved
    DEST_ORIG_T1 = os.path.join(BASE, "Original_T1_Scans")
    
    # Target directory for Strain data to be moved
    DEST_STRAIN = os.path.join(BASE, "Original_Strain_Scans")

    move_files_by_keyword(source_folder, DEST_ORIG_T1, ["_tMRIreg_T1.nii.gz"])
    move_files_by_keyword(source_folder, DEST_STRAIN, ["r5_E1_fit.nii.gz"])

if __name__ == "__main__":
    main()