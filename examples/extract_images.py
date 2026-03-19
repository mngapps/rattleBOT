"""
Example: Extract images from DOCX and PDF files.

Demonstrates how to:
  - extract_from_docx(): pull embedded images from DOCX using zipfile
  - extract_from_pdf(): pull embedded images from PDF using PyMuPDF (fitz)
  - Use argparse for CLI input file and output directory

Usage:
    python examples/extract_images.py input_file.docx -o output_dir/
    python examples/extract_images.py input_file.pdf -o output_dir/ --prefix my_product
    python examples/extract_images.py input_file.pdf --min-size 10000

Requirements:
    pip install PyMuPDF Pillow
"""

import argparse
import os
import sys
import zipfile

import fitz  # PyMuPDF

# Add project root to path (in case you need to import other utilities)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Minimum image size in bytes — filters out tiny icons and decorations
DEFAULT_MIN_SIZE = 5000


# ---------------------------------------------------------------------------
# DOCX extraction
# ---------------------------------------------------------------------------
def extract_from_docx(docx_path, output_folder, prefix="image", min_size=DEFAULT_MIN_SIZE):
    """Extract images from a DOCX file.

    DOCX files are ZIP archives. Images live under word/media/ inside the
    archive. This function extracts them, filters by size, and saves with
    a sequential naming scheme.

    Args:
        docx_path: Path to the .docx file.
        output_folder: Directory to save extracted images.
        prefix: Filename prefix for extracted images (default: "image").
        min_size: Minimum image size in bytes to keep (default: 5000).

    Returns:
        Number of images extracted.
    """
    os.makedirs(output_folder, exist_ok=True)
    count = 0

    # Allowed image extensions
    allowed_ext = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.emf', '.wmf')

    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            # Find all files in the word/media/ directory
            media_files = [f for f in z.namelist()
                           if f.startswith('word/media/')]

            for media_file in sorted(media_files):
                data = z.read(media_file)

                # Skip images smaller than the minimum size
                if len(data) < min_size:
                    continue

                # Check file extension
                ext = os.path.splitext(media_file)[1].lower()
                if ext not in allowed_ext:
                    continue

                # Convert EMF/WMF to PNG extension (data is kept as-is)
                if ext in ('.emf', '.wmf'):
                    ext = '.png'

                out_name = f"{prefix}_{count}{ext}"
                out_path = os.path.join(output_folder, out_name)
                with open(out_path, 'wb') as f:
                    f.write(data)
                count += 1

    except zipfile.BadZipFile:
        print(f"  WARNING: Could not open as ZIP: {docx_path}")
        return 0

    return count


# ---------------------------------------------------------------------------
# PDF extraction
# ---------------------------------------------------------------------------
def extract_from_pdf(pdf_path, output_folder, prefix="image", min_size=DEFAULT_MIN_SIZE):
    """Extract images from a PDF file using PyMuPDF.

    Iterates through all pages, extracts embedded images by xref,
    deduplicates, filters by size, and saves.

    Args:
        pdf_path: Path to the .pdf file.
        output_folder: Directory to save extracted images.
        prefix: Filename prefix for extracted images (default: "image").
        min_size: Minimum image size in bytes to keep (default: 5000).

    Returns:
        Number of images extracted.
    """
    os.makedirs(output_folder, exist_ok=True)
    count = 0

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"  WARNING: Could not open PDF: {pdf_path}: {e}")
        return 0

    # Track seen xrefs to avoid extracting the same image twice
    seen_xrefs = set()

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]

            # Skip duplicates (same image referenced on multiple pages)
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            if not base_image:
                continue

            image_bytes = base_image["image"]

            # Skip images smaller than the minimum size
            if len(image_bytes) < min_size:
                continue

            ext = base_image.get("ext", "png")
            if ext == "jpeg":
                ext = "jpg"

            out_name = f"{prefix}_{count}.{ext}"
            out_path = os.path.join(output_folder, out_name)
            with open(out_path, 'wb') as f:
                f.write(image_bytes)
            count += 1

    doc.close()
    return count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Extract images from DOCX or PDF files."
    )
    parser.add_argument(
        "input_file",
        help="Path to the input file (.docx or .pdf)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="Output directory for extracted images (default: <input_name>_images/)",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Filename prefix for extracted images (default: derived from input filename)",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=DEFAULT_MIN_SIZE,
        help=f"Minimum image size in bytes to keep (default: {DEFAULT_MIN_SIZE})",
    )

    args = parser.parse_args()

    input_file = args.input_file
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    # Determine file type
    ext = os.path.splitext(input_file)[1].lower()
    if ext not in ('.docx', '.pdf'):
        print(f"Error: Unsupported file type '{ext}'. Use .docx or .pdf")
        sys.exit(1)

    # Default output directory: <input_name>_images/
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = args.output_dir or f"{base_name}_images"
    prefix = args.prefix or base_name.lower().replace(" ", "_").replace("-", "_")

    print("=" * 60)
    print(f"Extracting images from: {input_file}")
    print(f"Output directory:       {output_dir}")
    print(f"Prefix:                 {prefix}")
    print(f"Min image size:         {args.min_size} bytes")
    print("=" * 60)

    # Extract based on file type
    if ext == '.docx':
        count = extract_from_docx(input_file, output_dir, prefix, args.min_size)
    else:
        count = extract_from_pdf(input_file, output_dir, prefix, args.min_size)

    print(f"\nExtracted {count} images to {output_dir}/")


if __name__ == "__main__":
    main()
