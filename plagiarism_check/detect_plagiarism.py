import os
import subprocess
from copydetect import CopyDetector

# --- CONFIGURATION ---
SUBMISSIONS_DIR = "./submissions"  # The folder containing all student folders
SKELETON_FILE = "empty_task.ipynb" # Your baseline notebook
REPORT_OUTPUT = "./plagiarism_report.html"

def prepare_files():
    print("Step 1: Converting Notebooks to Scripts...")
    # This finds every .ipynb in every subfolder and creates a .py version next to it
    subprocess.run(["jupyter", "nbconvert", "--to", "script", f"{SUBMISSIONS_DIR}/**/*.ipynb"], check=True)
    subprocess.run(["jupyter", "nbconvert", "--to", "script", SKELETON_FILE], check=True)

def run_detection():
    print("Step 2: Running Copydetect...")
    # Initialize detector
    # noise_t: minimum characters to flag (smaller = stricter)
    # display_t: only show pairs with >30% similarity
    detector = CopyDetector(
        test_dirs=[SUBMISSIONS_DIR],
        boilerplate_dirs=[os.path.dirname(SKELETON_FILE)],
        extensions=["py"],
        noise_t=25, 
        display_t=0.30, 
        out_file=REPORT_OUTPUT
    )
    
    detector.add_file(SKELETON_FILE.replace(".ipynb", ".py"), "boilerplate")
    detector.run()
    detector.generate_report()
    print(f"Finished! Open {REPORT_OUTPUT} to see results.")

if __name__ == "__main__":
    prepare_files()
    run_detection()
