from pathlib import Path
import os

from autovalidate.delete_files import confirm_deletions

# ===================== USER CONFIGURATION =====================

# Directory of your study
BASE = "path/to/study"

# Define directories to be deleted
Final_ROOT = os.path.join(BASE, "Final_Head")
Original = os.path.join(BASE, "Original_T1_Scans")

# =================== END USER CONFIGURATION ===================

if __name__ == "__main__":

    confirm_deletions(Final_ROOT, Original)