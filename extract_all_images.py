"""
Extract ALL images from ALL MECAL price list documents (DOCX and PDF).

Strategy:
  - For products with DOCX files: extract from DOCX (better quality)
  - For PDF-only products: extract from PDF using PyMuPDF
  - Skip products that already have an extraction directory
  - Filter out tiny images (< 5KB, likely icons/decorations)
  - Name images: {product_prefix}_{index}.{ext}
"""

import os
import re
import sys
import zipfile

import fitz  # PyMuPDF
from PIL import Image

MECAL_DIR = "source/pressta/pricelists/MECAL"
OUTPUT_DIR = os.path.join(MECAL_DIR, "extracted_images")

# Minimum image size in bytes to keep (filters out tiny icons)
MIN_IMAGE_SIZE = 5000

# Already-extracted product folder names (will be skipped)
ALREADY_EXTRACTED = {
    "mc304atlas_dpm",
    "mc304atlas_mmi",
    "mc305gianos_dpm",
    "mc305kosmos_dpm",
    "mc305kosmos_mmi",
    "mc307falcon_mmi",
    "sw453plug",
}


def filename_to_folder(filename):
    """Convert a source filename to a clean folder name.

    Examples:
        'MC 304 ARIEL-3A DPM_TED.docx' -> 'mc304ariel3a_dpm'
        'SW 453 ARGUS_TED.pdf' -> 'sw453argus'
        'MC 305 GIANOS TM DPM_TED.docx' -> 'mc305gianos_dpm'
        'DOMINO SSR 260_TED.pdf' -> 'domino_ssr260'
        'TDC 622 EdgeMaster -5A_TED.pdf' -> 'tdc622edgemaster5a'
        '2023_SMA-TECH-PESSTA DE_23039 (MC 316).docx' -> 'mc316swing'
    """
    # Remove extension
    name = os.path.splitext(filename)[0]
    # Remove _TED suffix
    name = re.sub(r'_TED$', '', name)

    # Special case for MC 316 doc
    if 'MC 316' in name or 'mc 316' in name.lower():
        return 'mc316swing'

    # Special case: N. 42686 is a quote, not a product
    if name.startswith('N.'):
        return None

    # Identify control type suffix (DPM, MMI, MDT, MTS, MQL, DBE, NSB-90)
    control_match = re.search(r'\b(DPM|MMI|MDT|MTS)\b', name)
    control_suffix = ''
    if control_match:
        control_suffix = '_' + control_match.group(1).lower()
        # Remove it from name for now
        name = name[:control_match.start()] + name[control_match.end():]

    # Remove "TM" (it's just a marker in some names)
    name = re.sub(r'\bTM\b', '', name)

    # Remove "PANELS" prefix (MC 304 PANELS ATLAS -> separate product)
    has_panels = 'PANELS' in name
    if has_panels:
        name = name.replace('PANELS', '')

    # Clean up: remove special chars, collapse spaces
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name)
    name = name.strip()

    # Split into parts
    parts = name.split()

    # Build folder name: join all parts, lowercase
    folder = ''.join(parts).lower()

    # Re-add panels prefix if it was there
    if has_panels:
        folder = folder.replace('atlas', 'panelsatlas')

    # Add control suffix
    folder += control_suffix

    return folder


def extract_from_docx(docx_path, output_folder, prefix):
    """Extract images from a DOCX file using zipfile."""
    os.makedirs(output_folder, exist_ok=True)
    count = 0

    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            media_files = [f for f in z.namelist()
                           if f.startswith('word/media/')]

            for media_file in sorted(media_files):
                data = z.read(media_file)
                if len(data) < MIN_IMAGE_SIZE:
                    continue

                # Get extension from original filename
                ext = os.path.splitext(media_file)[1].lower()
                if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.emf', '.wmf'):
                    continue

                # Convert EMF/WMF to PNG if needed
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


def extract_from_pdf(pdf_path, output_folder, prefix):
    """Extract images from a PDF file using PyMuPDF."""
    os.makedirs(output_folder, exist_ok=True)
    count = 0

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"  WARNING: Could not open PDF: {pdf_path}: {e}")
        return 0

    seen_xrefs = set()

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
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
            if len(image_bytes) < MIN_IMAGE_SIZE:
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


def main():
    print("=" * 70)
    print("MECAL Image Extraction — All Products")
    print("=" * 70)

    # Collect all source files
    all_files = os.listdir(MECAL_DIR)
    docx_files = sorted([f for f in all_files if f.endswith('.docx')])
    pdf_files = sorted([f for f in all_files if f.endswith('.pdf')])

    # Track which products have docx (to avoid duplicate PDF extraction)
    docx_products = set()
    results = []

    # --- Phase 1: Extract from DOCX files ---
    print(f"\n[Phase 1] Processing {len(docx_files)} DOCX files...")
    print("-" * 70)

    for fname in docx_files:
        folder_name = filename_to_folder(fname)
        if folder_name is None:
            print(f"  SKIP (not a product): {fname}")
            continue

        docx_products.add(folder_name)

        if folder_name in ALREADY_EXTRACTED:
            print(f"  SKIP (already extracted): {fname} -> {folder_name}/")
            continue

        output_folder = os.path.join(OUTPUT_DIR, folder_name)
        if os.path.exists(output_folder) and len(os.listdir(output_folder)) > 0:
            existing = len(os.listdir(output_folder))
            print(f"  SKIP (folder exists, {existing} files): {fname} -> {folder_name}/")
            continue

        filepath = os.path.join(MECAL_DIR, fname)
        print(f"  Extracting: {fname} -> {folder_name}/")
        count = extract_from_docx(filepath, output_folder, folder_name)
        print(f"    -> {count} images extracted")
        results.append((folder_name, 'docx', count))

    # --- Phase 2: Extract from PDF files (only if no DOCX version exists) ---
    print(f"\n[Phase 2] Processing PDF-only products...")
    print("-" * 70)

    for fname in pdf_files:
        folder_name = filename_to_folder(fname)
        if folder_name is None:
            print(f"  SKIP (not a product): {fname}")
            continue

        if folder_name in ALREADY_EXTRACTED:
            print(f"  SKIP (already extracted): {fname} -> {folder_name}/")
            continue

        if folder_name in docx_products:
            # Already handled from DOCX
            continue

        output_folder = os.path.join(OUTPUT_DIR, folder_name)
        if os.path.exists(output_folder) and len(os.listdir(output_folder)) > 0:
            existing = len(os.listdir(output_folder))
            print(f"  SKIP (folder exists, {existing} files): {fname} -> {folder_name}/")
            continue

        filepath = os.path.join(MECAL_DIR, fname)
        print(f"  Extracting: {fname} -> {folder_name}/")
        count = extract_from_pdf(filepath, output_folder, folder_name)
        print(f"    -> {count} images extracted")
        results.append((folder_name, 'pdf', count))

    # --- Summary ---
    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY")
    print("=" * 70)

    total_new = 0
    for folder, source, count in sorted(results):
        total_new += count
        print(f"  {folder:45s} ({source:4s}) -> {count:3d} images")

    print(f"\n  New products extracted: {len(results)}")
    print(f"  Total new images: {total_new}")
    print(f"  Previously extracted: {len(ALREADY_EXTRACTED)} products")

    # List all final product folders
    print(f"\n  All product folders:")
    for d in sorted(os.listdir(OUTPUT_DIR)):
        dp = os.path.join(OUTPUT_DIR, d)
        if os.path.isdir(dp):
            n = len([f for f in os.listdir(dp) if not f.startswith('.')])
            print(f"    {d:45s} {n:3d} images")


if __name__ == "__main__":
    main()
