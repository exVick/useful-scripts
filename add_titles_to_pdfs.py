import fitz  # PyMuPDF
import os
from pathlib import Path

def add_title_to_pdf(input_path, output_path, title_text, font_size=24, position=(50, 50), color=(0, 0, 0)):
    """
    Add a title to the upper left corner of each page in a PDF. 
    
    Args:
        input_path:  Path to input PDF file
        output_path: Path to save the modified PDF
        title_text: Text to add as title
        font_size: Size of the title text (default: 24)
        position: Tuple (x, y) for text position in pixels (default:  50, 50)
        color: RGB tuple for text color (default: black)
    """
    try:
        doc = fitz.open(input_path)
        
        for page_num, page in enumerate(doc, 1):
            # Insert text at specified position
            # Using 'helv' (Helvetica) which is a standard PDF font
            page.insert_text(
                position,
                title_text,
                fontsize=font_size,
                color=color,
                fontname="helv"  # Use standard Helvetica font
            )
            print(f"  ✓ Added title to page {page_num}")
        
        # Save the modified PDF
        doc. save(output_path)
        doc.close()
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {input_path}: {e}")
        return False

def process_pdfs_in_directory(directory_path, output_suffix="_titled", font_size=24, 
                               overwrite=False, position=(50, 80), color=(0, 0, 0)):
    """
    Process all PDF files in a directory and add their filename as title.
    
    Args:
        directory_path: Path to directory containing PDFs
        output_suffix: Suffix to add to output filenames (default: "_titled")
        font_size: Size of the title text (default: 24)
        overwrite: If True, overwrites original files (default: False)
        position: Tuple (x, y) for text position in pixels
        color: RGB tuple for text color (0-1 range for each component)
    """
    path = Path(directory_path)
    
    if not path.exists():
        print(f"❌ Error: Directory '{directory_path}' does not exist!")
        return
    
    if not path.is_dir():
        print(f"❌ Error:  '{directory_path}' is not a directory!")
        return
    
    # Find all PDF files
    pdf_files = list(path.glob("*.pdf")) + list(path.glob("*.PDF"))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in '{directory_path}'")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF file(s) in '{directory_path}'")
    print(f"⚙️  Settings: font_size={font_size}, position={position}, overwrite={overwrite}\n")
    
    success_count = 0
    
    for pdf_file in pdf_files:
        # Get filename without extension as title
        title = pdf_file.stem
        
        print(f"📄 Processing: {pdf_file.name}")
        print(f"   Title: '{title}'")
        
        # Determine output path
        if overwrite: 
            output_path = pdf_file
        else:
            output_path = pdf_file.parent / f"{pdf_file.stem}{output_suffix}.pdf"
        
        # Process the PDF
        if add_title_to_pdf(pdf_file, output_path, title, font_size, position, color):
            print(f"   ✅ Saved to: {output_path. name}\n")
            success_count += 1
        else: 
            print()
    
    print(f"{'='*60}")
    print(f"✨ Processing complete! {success_count}/{len(pdf_files)} files processed successfully.")
    if not overwrite:
        print(f"   Original files preserved.  New files have '{output_suffix}' suffix.")

def main():
    """Main function with example usage and configuration."""
    
    # ==================== CONFIGURATION ====================
    
    # Path to directory containing PDFs
    pdf_directory = input("Enter the path to the directory containing PDFs: ").strip()
    
    # Or hardcode the path:
    # pdf_directory = "/path/to/your/pdfs"
    
    # Font size for the title
    FONT_SIZE = 8
    
    # Position (x, y) in pixels from top-left corner
    # For your 2481 x 3508 pixel pages, adjust as needed
    POSITION = (5, FONT_SIZE+2)  # from left, from top
    
    # Text color (R, G, B) - values from 0 to 1
    COLOR = (0, 0, 0)  # Black
    # COLOR = (1, 0, 0)  # Red
    # COLOR = (0, 0, 1)  # Blue
    
    # Suffix for output files (ignored if overwrite=True)
    OUTPUT_SUFFIX = "_titled"
    
    # Set to True to overwrite original files (be careful!)
    OVERWRITE = False
    
    # =======================================================
    
    process_pdfs_in_directory(
        pdf_directory,
        output_suffix=OUTPUT_SUFFIX,
        font_size=FONT_SIZE,
        overwrite=OVERWRITE,
        position=POSITION,
        color=COLOR
    )

if __name__ == "__main__":
    main()