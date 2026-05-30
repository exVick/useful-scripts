# Plagiarism Check Pipeline

This repo provides a two-stage workflow for notebook-based assignments:
1) Convert notebooks to .py or .md.
2) Optionally filter to specific exercises and/or subtract boilerplate.
3) Run Copydetect to generate an HTML report.

The main entry point is detect_plagiarism.py. A standalone preprocessing script is also available for filtering converted files before you run detection or for one-off cleanup.

## How the pipeline works

Sequence in the main script:
1) Full conversion from .ipynb to .py or .md.
2) Optional keep-exercises filtering, which rewrites the converted files in place.
3) Optional subtract-boilerplate, which rewrites the converted submission files in place.
4) Copydetect runs on the final, rewritten files and generates the report.

Important details:
- Conversion only runs if the target .py/.md file does not exist, unless --force-reconvert is used.
- keep-exercises filtering happens after conversion, not during conversion.
- subtract-boilerplate runs after keep-exercises and mutates the same converted submission files.

## CLI arguments (detect_plagiarism.py)

Required:
- --submissions-dir
  Folder containing student submissions (.ipynb). The script searches recursively.
- --boilerplate-dir
  Folder containing the boilerplate notebook and converted boilerplate files.
  The boilerplate directory must contain exactly one .ipynb file.
- --report-output
  Output path for the Copydetect report (HTML is generated at the end).

Optional:
- --output-format {py, md}
  Output file type used for conversion and detection. Default: py.
  If py, notebook cell markers like "# In[1]:" are removed.
- --keep-exercises 1,4
  Comma-separated exercise numbers to keep. Filtering happens after conversion
  and rewrites the converted files in place.
- --subtract-boilerplate
  Removes boilerplate chunks and boilerplate lines from converted submission
  files in place. When this is enabled, Copydetect does not load boilerplate
  files (to avoid double subtraction).
- --guarantee-t 60
  Minimum copied characters to guarantee a match. Default: 60.
- --noise-t 60
  Ignore copied segments below this threshold. Default: 60.
  If guarantee-t < noise-t, guarantee-t is bumped up to noise-t.
- --display-t 0.85
  Similarity threshold shown in the report. Default: 0.85.
- --force-reconvert
  Always reconvert .ipynb to .py/.md, even if converted files already exist.

## When to use the standalone preprocessing script

Use preprocess_exercises.py when you want to filter already-converted files
without running the full detection pipeline. For example, you already converted notebooks and want to re-filter for different exercises.

## Usage examples

Standalone preprocessing script usage:
`python preprocess_exercises.py --target-dir "/path/to/converted/files" --extension py --keep-exercises 1,4`

Main pipeline usage example:
`python detect_plagiarism.py --submissions-dir "/path/submissions" --boilerplate-dir "/path/boilerplate" --report-output "/path/report.html" --output-format md --keep-exercises 1,4`
