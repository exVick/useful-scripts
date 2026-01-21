import fitz  # PyMuPDF
import os
from pathlib import Path

def add_title_to_pdf(input_path, output_path, title_text, font_size=24, position=(50, 50), color=(0, 0, 0)):
    """
    Add a title to the upper left corner of each page in a PDF.  
    
    Args: 
        input_path:  Path to input PDF file
        output_path:  Path to save the modified PDF
        title_text: Text to add as title
        font_size:  Size of the title text (default:   24)
        position: Tuple (x, y) for text position in pixels (default:  50, 50)
        color: RGB tuple for text color (default:  black)
    """
    try:
        doc = fitz. open(input_path)
        
        for page_num, page in enumerate(doc, 1):
            # Insert text at specified position
            page.insert_text(
                position,
                title_text,
                fontsize=font_size,
                color=color,
                fontname="helv"  # Use standard Helvetica font
            )
        
        # Save the modified PDF
        doc. save(output_path)
        doc.close()
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {input_path}: {e}")
        return False

def process_pdfs_in_directory(directory_path, font_size=24, position=(50, 80), color=(0, 0, 0)):
    """
    Process all PDF files in a directory and add their filename as title.
    Creates a 'titled' subfolder for output files.
    
    Args:
        directory_path: Path to directory containing PDFs
        font_size: Size of the title text (default: 24)
        position: Tuple (x, y) for text position in pixels
        color:  RGB tuple for text color (0-1 range for each component)
    """
    path = Path(directory_path)
    
    if not path.exists():
        print(f"❌ Error: Directory '{directory_path}' does not exist!")
        return
    
    if not path.is_dir():
        print(f"❌ Error:  '{directory_path}' is not a directory!")
        return
    
    # Create 'titled' subdirectory
    output_dir = path / "titled"
    try:
        output_dir.mkdir(exist_ok=True)
        print(f"📁 Output directory: {output_dir}")
    except Exception as e: 
        print(f"❌ Error creating output directory: {e}")
        return
    
    # Find all PDF files in the main directory (not in subdirectories)
    pdf_files = list(path.glob("*.pdf")) + list(path.glob("*.PDF"))
    
    if not pdf_files: 
        print(f"⚠️  No PDF files found in '{directory_path}'")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF file(s) in '{directory_path}'")
    print(f"⚙️  Settings:  font_size={font_size}, position={position}\n")
    
    success_count = 0
    
    for pdf_file in pdf_files:
        # Get filename without extension as title
        title = pdf_file.stem
        
        print(f"📄 Processing:  {pdf_file.name}")
        print(f"   Title:  '{title}'")
        
        # Output to 'titled' subdirectory with same filename
        output_path = output_dir / pdf_file.name
        
        # Process the PDF
        if add_title_to_pdf(pdf_file, output_path, title, font_size, position, color):
            print(f"   ✅ Saved to:  titled/{output_path.name}\n")
            success_count += 1
        else:
            print()
    
    print(f"{'='*60}")
    print(f"✨ Processing complete! {success_count}/{len(pdf_files)} files processed successfully.")
    print(f"   All titled PDFs saved in:  {output_dir}")

def get_font_size_from_user():
    """
    Prompt user for font size with validation. 
    """
    while True: 
        try:
            font_size_input = input("Enter font size (default 30, press Enter to use default): ").strip()
            
            # Use default if empty
            if not font_size_input:
                return 30
            
            font_size = int(font_size_input)
            
            if font_size <= 0:
                print("❌ Font size must be a positive number.  Please try again.")
                continue
            
            if font_size > 200:
                confirm = input(f"⚠️  Font size {font_size} is very large. Continue?  (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            
            return font_size
            
        except ValueError: 
            print("❌ Invalid input. Please enter a number.")

def main():
    """Main function with user prompts for path and font size."""
    
    print("=" * 60)
    print("PDF Title Adder - Add filename as title to each page")
    print("=" * 60)
    print()
    
    # Get directory path from user
    pdf_directory = input("Enter the path to the directory containing PDFs:  ").strip()
    
    # Remove quotes if user wrapped path in quotes
    pdf_directory = pdf_directory.strip('"').strip("'")
    
    if not pdf_directory:
        print("❌ Error: No path provided.")
        return
    
    # Get font size from user
    font_size = get_font_size_from_user()
    
    print()
    
    # ==================== CONFIGURATION ====================
    
    # Position (x, y) in pixels from top-left corner
    # For your 2481 x 3508 pixel pages, adjust as needed
    POSITION = (5, font_size+2)  # from left, from top
    
    # Text color (R, G, B) - values from 0 to 1
    COLOR = (0, 0, 0)  # Black
    # COLOR = (1, 0, 0)  # Red
    # COLOR = (0, 0, 1)  # Blue
    
    # =======================================================
    
    process_pdfs_in_directory(
        pdf_directory,
        font_size=font_size,
        position=POSITION,
        color=COLOR
    )

if __name__ == "__main__": 
    main()