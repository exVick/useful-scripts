import os
import sys
import subprocess
from pathlib import Path
from tqdm import tqdm
from copydetect import CopyDetector

# --- CONFIGURATION ---
SUBMISSIONS_DIR = "./submissions"
BOILERPLATE_DIR = "./boilerplate"     # FIXED: Dedicated boilerplate directory
SKELETON_FILE = "empty_task.ipynb"    # Assumed to be inside BOILERPLATE_DIR
REPORT_OUTPUT = "./plagiarism_report"

def prepare_files(force_reconvert=False):
    print(f"Step 1: Converting Notebooks to Scripts {'(FORCE MODE)' if force_reconvert else '(Skipping existing)'}...")
    
    # 1. Check if boilerplate directory and file exist
    skeleton_path = Path(BOILERPLATE_DIR) / SKELETON_FILE
    if not skeleton_path.exists():
        print(f"ERROR: Could not find {skeleton_path}.")
        print(f"Please create a '{BOILERPLATE_DIR}' folder and put '{SKELETON_FILE}' inside it.")
        return False

    # 2. Convert the skeleton file
    skeleton_py = skeleton_path.with_suffix('.py')
    if force_reconvert or not skeleton_py.exists():
        subprocess.run(
            ["jupyter", "nbconvert", "--to", "script", str(skeleton_path)],
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            check=True
        )

    # 3. Find all student notebooks
    notebooks = list(Path(SUBMISSIONS_DIR).rglob("*.ipynb"))
    if not notebooks:
        print(f"No .ipynb files found in {SUBMISSIONS_DIR}")
        return False

    # 4. Convert student files
    for nb in tqdm(notebooks, desc="Converting", unit="file", leave=True):
        target_file = nb.with_suffix('.py')
        
        if force_reconvert or not target_file.exists():
            subprocess.run(
                ["jupyter", "nbconvert", "--to", "script", str(nb)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
    return True

def run_detection():
    print("\nStep 2: Running Copydetect...")
    
    detector = CopyDetector(
        test_dirs=[SUBMISSIONS_DIR],
        boilerplate_dirs=[BOILERPLATE_DIR],  # FIXED: Now points directly to the isolated folder
        extensions=["py"],
        noise_t=25, 
        display_t=0.30, 
        out_file=REPORT_OUTPUT
    )
    
    detector.run()
    detector.generate_html_report() 
    print(f"\nFinished! Open {REPORT_OUTPUT}.html to see results.")

if __name__ == "__main__":
    # Check if the user passed the --force flag in the terminal
    force_flag = "--force" in sys.argv
    
    if prepare_files(force_reconvert=force_flag):
        run_detection()