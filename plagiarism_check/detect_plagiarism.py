import os
import subprocess
from pathlib import Path
from tqdm import tqdm
from copydetect import CopyDetector

# --- CONFIGURATION ---
SUBMISSIONS_DIR = "./submissions"  # The folder containing all student folders
SKELETON_FILE = "empty_task.ipynb" # Your baseline notebook
REPORT_OUTPUT = "./plagiarism_report.html"

def prepare_files():
    print("Step 1: Converting Notebooks to Scripts...")
    
    # 1. Convert the skeleton file first (silently)
    subprocess.run(
        ["jupyter", "nbconvert", "--to", "script", SKELETON_FILE],
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL,
        check=True
    )

    # 2. Find all student notebooks in all subfolders
    notebooks = list(Path(SUBMISSIONS_DIR).rglob("*.ipynb"))
    
    if not notebooks:
        print(f"No .ipynb files found in {SUBMISSIONS_DIR}")
        return False

    # 3. Convert them one by one with a progress bar
    for nb in tqdm(notebooks, desc="Converting", unit="file", leave=True):
        subprocess.run(
            ["jupyter", "nbconvert", "--to", "script", str(nb)],
            stdout=subprocess.DEVNULL, # Suppresses standard output
            stderr=subprocess.DEVNULL, # Suppresses error/warning noise
            check=True
        )
    return True

def run_detection():
    print("\nStep 2: Running Copydetect...")
    
    detector = CopyDetector(
        test_dirs=[SUBMISSIONS_DIR],
        boilerplate_dirs=[os.path.dirname(SKELETON_FILE) if os.path.dirname(SKELETON_FILE) else "."],
        extensions=["py"],
        noise_t=25, 
        display_t=0.30, 
        out_file=REPORT_OUTPUT
    )
    
    skeleton_py = SKELETON_FILE.replace(".ipynb", ".py")
    detector.add_file(skeleton_py, "boilerplate")
    
    detector.run()
    
    # FIXED: Correct method name
    detector.generate_html_report() 
    print(f"\nFinished! Open {REPORT_OUTPUT}.html to see results.")

if __name__ == "__main__":
    if prepare_files():
        run_detection()