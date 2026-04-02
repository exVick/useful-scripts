import os
import sys
import subprocess
import re
import argparse
from pathlib import Path
from tqdm import tqdm
from copydetect import CopyDetector
from preprocess_exercises import (
    parse_exercise_list,
    preprocess_directory,
    subtract_boilerplate_from_submissions,
)

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

def prepare_files(submissions_dir, boilerplate_dir, output_format="py", force_reconvert=False):
    if output_format == "md":
        print(f"Step 1: Converting Notebooks to Markdown{' (FORCE MODE)' if force_reconvert else ''}...")
    else:
        print(f"Step 1: Converting Notebooks to Scripts{' (FORCE MODE)' if force_reconvert else ''}...")
    
    # 1. Convert and clean the skeleton file
    skeleton_notebooks = list(Path(boilerplate_dir).glob("*.ipynb"))
    if not skeleton_notebooks:
        print(f"ERROR: No .ipynb file found in {boilerplate_dir}.")
        sys.exit(1)
    if len(skeleton_notebooks) > 1:
        print(
            f"ERROR: Expected exactly 1 .ipynb in {boilerplate_dir}, "
            f"but found {len(skeleton_notebooks)}."
        )
        sys.exit(1)

    skeleton_path = skeleton_notebooks[0]

    if output_format == "md":
        target_suffix = ".md"
        convert_to = "markdown"
    else:
        target_suffix = ".py"
        convert_to = "script"

    skeleton_target = skeleton_path.with_suffix(target_suffix)
    if force_reconvert or not skeleton_target.exists():
        subprocess.run(
            ["jupyter", "nbconvert", "--to", convert_to, str(skeleton_path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )

    if output_format == "py":
        clean_jupyter_noise(skeleton_target) # Only needed for python conversion

    # 2. Find and convert student files
    notebooks = list(Path(submissions_dir).rglob("*.ipynb"))
    if not notebooks:
        print(f"No .ipynb files found in {submissions_dir}")
        return False

    for nb in tqdm(notebooks, desc="Converting & Cleaning", unit="file", leave=True):
        target_file = nb.with_suffix(target_suffix)
        if force_reconvert or not target_file.exists():
            subprocess.run(
                ["jupyter", "nbconvert", "--to", convert_to, str(nb)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
            )
        if output_format == "py":
            clean_jupyter_noise(target_file) # Only needed for python conversion
        
    return True

def run_detection(
    submissions_dir,
    boilerplate_dir,
    report_output,
    output_format="py",
    guarantee_t=60,
    noise_t=60,
    display_t=0.85,
    include_boilerplate=True,
):
    print("\nStep 2: Running Copydetect...")

    if guarantee_t < noise_t:
        print(
            f"Warning: guarantee_t ({guarantee_t}) was less than noise_t ({noise_t}). "
            f"Setting guarantee_t = noise_t ({noise_t})."
        )
        guarantee_t = noise_t
    
    detector = CopyDetector(
        test_dirs=[submissions_dir],
        extensions=[output_format],
        guarantee_t=guarantee_t,
        noise_t=noise_t,
        display_t=display_t,
        out_file=report_output
    )
    
    if include_boilerplate:
        # EXPLICITLY LOAD BOILERPLATE (Bulletproof method)
        added_boilerplates = 0
        for b_file in Path(boilerplate_dir).rglob(f"*.{output_format}"):
            detector.add_file(str(b_file), "boilerplate")
            added_boilerplates += 1

        print(f"--> Loaded {added_boilerplates} boilerplate file(s).")
        if added_boilerplates == 0:
            print("CRITICAL WARNING: No boilerplate loaded! Check your folder paths.")
            sys.exit(1)
    else:
        print("--> Boilerplate loading disabled because subtraction mode is enabled.")
        
    detector.run()
    detector.generate_html_report() 
    print(f"\nFinished! Open {report_output} to see results.")


def preprocess_before_detection(submissions_dir, boilerplate_dir, output_format, keep_exercises_arg):
    if not keep_exercises_arg:
        print("Step 1.5: Preprocessing skipped (no --keep-exercises provided).")
        return

    keep_exercises = parse_exercise_list(keep_exercises_arg)
    selected = ", ".join(str(x) for x in sorted(keep_exercises))
    print(f"Step 1.5: Keeping exercises [{selected}] in .{output_format} files...")

    submissions_result = preprocess_directory(submissions_dir, output_format, keep_exercises)
    boilerplate_result = preprocess_directory(boilerplate_dir, output_format, keep_exercises)

    print(
        "--> Submissions preprocessing: "
        f"processed={submissions_result['processed']}, "
        f"changed={submissions_result['changed']}, "
        f"without_headers={submissions_result['without_headers']}"
    )
    print(
        "--> Boilerplate preprocessing: "
        f"processed={boilerplate_result['processed']}, "
        f"changed={boilerplate_result['changed']}, "
        f"without_headers={boilerplate_result['without_headers']}"
    )


def subtract_boilerplate_before_detection(submissions_dir, boilerplate_dir, output_format, subtract_boilerplate):
    if not subtract_boilerplate:
        print("Step 1.6: Boilerplate subtraction skipped.")
        return

    print(f"Step 1.6: Subtracting boilerplate content from .{output_format} submission files...")
    result = subtract_boilerplate_from_submissions(
        submissions_dir=submissions_dir,
        boilerplate_dir=boilerplate_dir,
        extension=output_format,
    )

    if result["boilerplate_files"] == 0:
        print("ERROR: No converted boilerplate files found for subtraction.")
        sys.exit(1)

    print(
        "--> Subtraction result: "
        f"processed={result['processed']}, "
        f"changed={result['changed']}, "
        f"chunk_replacements={result['chunk_replacements']}, "
        f"line_replacements={result['line_replacements']}"
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert notebooks to Python and run plagiarism detection with Copydetect."
    )
    parser.add_argument("--submissions-dir", required=True, help="Path to the folder containing student submissions.")
    parser.add_argument("--boilerplate-dir", required=True, help="Path to the folder containing boilerplate files.")
    parser.add_argument("--report-output", required=True, help="Output report path prefix for Copydetect.")
    parser.add_argument(
        "--output-format",
        choices=["py", "md"],
        default="py",
        help="File format used for conversion and detection (default: py)."
    )
    parser.add_argument(
        "--keep-exercises",
        default="",
        help="Comma-separated exercise numbers to keep before detection (example: 1,4)."
    )
    parser.add_argument(
        "--subtract-boilerplate",
        action="store_true",
        help="Subtract boilerplate content from submissions before detection. Disabled by default."
    )
    parser.add_argument(
        "--guarantee-t",
        type=int,
        default=60,
        help="Minimum copied characters to guarantee a match (default: 60)."
    )
    parser.add_argument(
        "--noise-t",
        type=int,
        default=60,
        help="Ignore copied segments below this threshold (default: 60)."
    )
    parser.add_argument(
        "--display-t",
        type=float,
        default=0.85,
        help="Similarity threshold shown in the report (default: 0.85)."
    )
    parser.add_argument(
        "--force-reconvert",
        action="store_true",
        help="Reconvert all notebooks even if .py files already exist."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    prepare_files(
        submissions_dir=args.submissions_dir,
        boilerplate_dir=args.boilerplate_dir,
        output_format=args.output_format,
        force_reconvert=args.force_reconvert,
    )
    preprocess_before_detection(
        submissions_dir=args.submissions_dir,
        boilerplate_dir=args.boilerplate_dir,
        output_format=args.output_format,
        keep_exercises_arg=args.keep_exercises,
    )
    subtract_boilerplate_before_detection(
        submissions_dir=args.submissions_dir,
        boilerplate_dir=args.boilerplate_dir,
        output_format=args.output_format,
        subtract_boilerplate=args.subtract_boilerplate,
    )
    run_detection(
        submissions_dir=args.submissions_dir,
        boilerplate_dir=args.boilerplate_dir,
        report_output=args.report_output,
        output_format=args.output_format,
        guarantee_t=args.guarantee_t,
        noise_t=args.noise_t,
        display_t=args.display_t,
        include_boilerplate=not args.subtract_boilerplate,
    )