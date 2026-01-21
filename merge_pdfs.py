#!/usr/bin/env python3
"""
merge_pdfs_robust.py

A robust script to merge PDF files, handling "Stream has ended unexpectedly"
and "NullObject" errors by reading files in non-strict mode.
"""
import os
import sys
import glob
import re
from PyPDF2 import PdfMerger

# Try to import PdfReader (newer PyPDF2), fallback to PdfFileReader (older PyPDF2)
try:
    from PyPDF2 import PdfReader
except ImportError:
    from PyPDF2 import PdfFileReader as PdfReader

def natural_sort_key(s):
    """
    Key for natural sorting of strings.
    Splits 'Page 1.pdf' into ['Page ', 1, '.pdf'] for correct ordering.
    """
    filename = os.path.basename(s)
    parts = re.split(r'(\d+)', filename)
    converted_parts = []
    for part in parts:
        if part.isdigit():
            converted_parts.append(int(part))
        else:
            converted_parts.append(part.lower())
    return converted_parts

def merge_pdfs_in_folder(folder_path: str, output_name: str = "ALL.pdf"):
    if not os.path.isdir(folder_path):
        print(f"Error: Directory '{folder_path}' does not exist.")
        sys.exit(1)

    # Find and exclude existing output
    pattern = os.path.join(folder_path, "*.pdf")
    pdf_files = [f for f in glob.glob(pattern) if os.path.isfile(f)]
    output_path = os.path.join(folder_path, output_name)
    pdf_files = [f for f in pdf_files if os.path.abspath(f) != os.path.abspath(output_path)]

    if not pdf_files:
        print("No PDF files found to merge.")
        sys.exit(0)

    # Sort files
    pdf_files.sort(key=natural_sort_key)

    merger = PdfMerger()
    file_handles = [] # Keep files open until merge is done

    try:
        for pdf in pdf_files:
            print(f"Adding {os.path.basename(pdf)}...")
            
            # Open file in binary read mode
            f = open(pdf, 'rb')
            file_handles.append(f)
            
            try:
                # strict=False is the specific fix for "Stream has ended unexpectedly"
                # and "NullObject" errors. It attempts to repair malformed PDFs.
                reader = PdfReader(f, strict=False)
                merger.append(reader)
            except Exception as e:
                print(f"  [WARNING] Could not read {os.path.basename(pdf)}: {e}")
                print(f"  Skipping this file.")

        print("Writing merged PDF...")
        merger.write(output_path)
        print(f"Merge complete! Saved as '{output_name}'.")

    except Exception as e:
        print(f"Failed to write merged PDF: {e}")
    finally:
        merger.close()
        # Close all file handles
        for f in file_handles:
            f.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python merge_pdfs.py /path/to/folder")
        sys.exit(1)

    folder = sys.argv[1]
    merge_pdfs_in_folder(folder)

if __name__ == "__main__":
    main()