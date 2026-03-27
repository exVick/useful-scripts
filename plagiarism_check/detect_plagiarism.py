import os
import sys
import subprocess
import re
from pathlib import Path
from tqdm import tqdm
from copydetect import CopyDetector

# --- CONFIGURATION ---
SUBMISSIONS_DIR = "./submissions"
BOILERPLATE_DIR = "./boilerplate"     
SKELETON_FILE = "A1_empty.ipynb"   # Ensure this matches the name in your boilerplate folder
REPORT_OUTPUT = "./plagiarism_report"

def clean_jupyter_noise(filepath):
    """Removes the '# In[...]:' lines that break boilerplate matching."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex to strip "# In[9]:", "# In[ ]:", etc.
        cleaned_content = re.sub(r'# In\[.*?\]:\n', '', content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
    except Exception as e:
        pass # Skip if file can't be read

def prepare_files(force_reconvert=False):
    print(f"Step 1: Converting Notebooks to Scripts {'(FORCE MODE)' if force_reconvert else '(Skipping existing)'}...")
    
    # 1. Convert and clean the skeleton file
    skeleton_path = Path(BOILERPLATE_DIR) / SKELETON_FILE
    if not skeleton_path.exists():
        print(f"ERROR: Could not find {skeleton_path}.")
        sys.exit(1)

    skeleton_py = skeleton_path.with_suffix('.py')
    if force_reconvert or not skeleton_py.exists():
        subprocess.run(
            ["jupyter", "nbconvert", "--to", "script", str(skeleton_path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
    clean_jupyter_noise(skeleton_py) # Clean the boilerplate

    # 2. Find and convert student files
    notebooks = list(Path(SUBMISSIONS_DIR).rglob("*.ipynb"))
    if not notebooks:
        print(f"No .ipynb files found in {SUBMISSIONS_DIR}")
        return False

    for nb in tqdm(notebooks, desc="Converting & Cleaning", unit="file", leave=True):
        target_file = nb.with_suffix('.py')
        if force_reconvert or not target_file.exists():
            subprocess.run(
                ["jupyter", "nbconvert", "--to", "script", str(nb)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
            )
        clean_jupyter_noise(target_file) # Clean the student file
        
    return True

def run_detection():
    print("\nStep 2: Running Copydetect...")
    
    detector = CopyDetector(
        test_dirs=[SUBMISSIONS_DIR],
        extensions=["py"],
        noise_t=60,         # Keep this high to ignore 1-liners
        display_t=0.85,     # Keep this high for a clean report
        out_file=REPORT_OUTPUT
    )
    
    # EXPLICITLY LOAD BOILERPLATE (Bulletproof method)
    added_boilerplates = 0
    for b_file in Path(BOILERPLATE_DIR).rglob("*.py"):
        detector.add_file(str(b_file), "boilerplate")
        added_boilerplates += 1
        
    print(f"--> Loaded {added_boilerplates} boilerplate file(s).")
    if added_boilerplates == 0:
        print("CRITICAL WARNING: No boilerplate loaded! Check your folder paths.")
        sys.exit(1)
        
    detector.run()
    detector.generate_html_report() 
    print(f"\nFinished! Open {REPORT_OUTPUT}.html to see results.")

if __name__ == "__main__":
    # Always force reconvert once to ensure the regex cleaner runs on all files!
    prepare_files(force_reconvert=True) 
    run_detection()