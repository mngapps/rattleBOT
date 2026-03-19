"""
Extract ALL images from ALL MECAL PDFs with descriptive section-based names.

Uses page.get_image_rects(xref) to correctly determine which page each
image actually appears on, then names images based on their section context.

Replaces previous sequential and incorrectly-named extractions.
"""

import os
import re
import sys
from collections import defaultdict

import fitz  # PyMuPDF
from PIL import Image, ImageEnhance

MECAL_DIR = "source/pressta/pricelists/MECAL"
EXTRACTED_DIR = os.path.join(MECAL_DIR, "extracted_images")
MIN_IMAGE_SIZE = 5000

# Products already configured with upload scripts - don't touch
SKIP_PRODUCTS = {
    "mc304atlas_dpm", "mc304atlas_mmi",
    "mc305gianos_dpm", "mc305kosmos_dpm", "mc305kosmos_mmi",
    "mc307falcon_mmi", "sw453plug",
}

SECTION_KEYWORDS = [
    ('Beschreibung und Eigenschaft', 'beschreibung'),
    ('Hauptansichten', 'hauptansichten'),
    ('Elektrospindel. [Auf Anfrage]', 'elektrospindel_optional'),
    ('Elektrospindel. [Standard]', 'elektrospindel_standard'),
    ('Elektrospindel', 'elektrospindel'),
    ('Verstärkte Frässpindel', 'verstaerkte_fraesspindel'),
    ('Frässpindel', 'fraesspindel'),
    ('Spindel', 'spindel'),
    ('Achsenhub', 'achsenhub'),
    ('Werkzeugmagazin', 'werkzeugmagazin'),
    ('Werkzeugzubehör HSK', 'werkzeugzubehoer_hsk'),
    ('Werkzeugzubehör ISO', 'werkzeugzubehoer_iso'),
    ('Werkzeugzubehör', 'werkzeugzubehoer'),
    ('Standardwerkzeug', 'standardwerkzeuge'),
    ('Werkzeuge', 'werkzeuge'),
    ('Werkzeugkühlung', 'werkzeugkuehlung'),
    ('Abkühlung der Werkzeuge', 'kuehlung'),
    ('Abkühlung', 'kuehlung'),
    ('MQL. Minimalmengen', 'mql_kuehlung'),
    ('MQL', 'mql_kuehlung'),
    ('Umfangsschutz', 'umfangsschutz'),
    ('Sicherheit und Schutz', 'sicherheit'),
    ('Sicherheit', 'sicherheit'),
    ('Umzäunung', 'umzaeunung'),
    ('Profilspanner', 'profilspanner'),
    ('Werkstückblockierung', 'werkstueckblockierung'),
    ('Schraubstock', 'schraubstock'),
    ('Referenzanschläge', 'referenzanschlaege'),
    ('Referenzanschlag', 'referenzanschlag'),
    ('Bewegliche Rollenbahn', 'rollenbahn'),
    ('Rollenbahn', 'rollenbahn'),
    ('Reststückförderer', 'reststueckfoerderer'),
    ('Kanal für die Reststückabführung', 'reststueckkanal'),
    ('Reststück', 'reststueck'),
    ('Förderer', 'foerderer'),
    ('Sägeeinheit', 'saegeeinheit'),
    ('Sägediagramm', 'saegediagramm'),
    ('Eigenschaft des Sägeblatts', 'saegeblatt'),
    ('Sägeblatt', 'saegeblatt'),
    ('Neigungspositionen', 'neigungspositionen'),
    ('Neigung', 'neigung'),
    ('Aufstellplan', 'aufstellplan'),
    ('Technische Zeichnung', 'technische_zeichnung'),
    ('Steuer- und Kontrolleinheit', 'steuereinheit'),
    ('Steuereinheit', 'steuereinheit'),
    ('Bedienoberfläche', 'hmi'),
    ('HMI', 'hmi'),
    ('Barcodeleser', 'barcodeleser'),
    ('Barcode', 'barcodeleser'),
    ('Netzwerkkarte', 'netzwerk'),
    ('Teleservice', 'teleservice'),
    ('3D-Simulator', 'cam_simulator'),
    ('Simulator', 'cam_simulator'),
    ('CAM', 'cam_software'),
    ('CADLINK', 'cadlink'),
    ('Betriebssoftware', 'betriebssoftware'),
    ('Software', 'software'),
    ('Schaltschrank', 'schaltschrank'),
    ('Absauganlage', 'absauganlage'),
    ('Absaug', 'absauganlage'),
    ('Etikettendrucker', 'etikettendrucker'),
    ('Drucker', 'drucker'),
    ('Verpackung', 'verpackung'),
    ('Normen', 'normen'),
    ('Versorgung', 'versorgung'),
    ('Struktur', 'struktur'),
    ('Maschinenunterbau', 'unterbau'),
    ('Arbeitsplatte', 'arbeitsplatte'),
    ('Profil-Halter', 'profilhalter'),
    ('Stützvorrichtung des Profils', 'stuetzvorrichtung'),
    ('Zwischenzeitliche Unterstützung', 'zwischenstuetzung'),
    ('Ermittlung der Profilhöhe', 'profilhoehe'),
    ('Profilhöhe', 'profilhoehe'),
    ('Positionierung der mobilen', 'positionierung_mobil'),
    ('Komponenten der strukturellen', 'strukturkonfiguration'),
    ('Komponenten', 'komponenten'),
    ('Hard- und Softwarezubehör', 'hard_software'),
    ('Hardwarezubehör', 'hardware'),
    ('Mechanisches Zubehör', 'mech_zubehoer'),
    ('Zubehör OEM', 'zubehoer_oem'),
    ('Zubehör', 'zubehoer'),
    ('Komposition der Basismaschine', 'basismaschine'),
    ('Komposition', 'komposition'),
    ('Gewährleistung', 'garantie'),
    ('Garantie', 'garantie'),
    ('Ausbildung', 'ausbildung'),
    ('Installations- und Abnahme', 'installation'),
    ('Installation', 'installation'),
    ('Lieferdienst', 'lieferdienst'),
    ('Schmierstoff', 'schmierstoffe'),
    ('Kühlmittel', 'kuehlmittel'),
    ('Maßeinheit', 'masseinheit'),
    ('Modellvariante', 'modellvarianten'),
    ('Haupteinheit', 'haupteinheit'),
    ('Gegenseitig ausgeschlossener', 'ausgeschlossen'),
    ('Operative Funktionsweise', 'funktionsweisen'),
    ('Bearbeitungsflächen', 'bearbeitungsflaechen'),
]


def detect_section_for_page(page):
    """Detect the section heading for a PDF page."""
    blocks = page.get_text("blocks")
    text_blocks = []
    for b in blocks:
        if b[6] == 0:
            t = b[4].strip()
            if t and len(t) > 2:
                text_blocks.append(t)

    combined = '\n'.join(text_blocks)
    for keyword, name in SECTION_KEYWORDS:
        if keyword in combined:
            return name

    return ''


def filename_to_folder(filename):
    """Convert source filename to folder name (same as extract_all_images.py)."""
    from extract_all_images import filename_to_folder as f2f
    return f2f(filename)


def create_shadow(src_path, dst_path):
    """Create greyed-out version."""
    try:
        img = Image.open(src_path).convert("RGBA")
        gray = ImageEnhance.Color(img).enhance(0.0)
        dimmed = ImageEnhance.Brightness(gray).enhance(0.85)
        white = Image.new("RGBA", dimmed.size, (255, 255, 255, 255))
        faded = Image.blend(white, dimmed, alpha=0.5)
        faded.convert("RGB").save(dst_path, "JPEG", quality=90)
        return True
    except Exception:
        return False


def extract_product_from_pdf(pdf_path, product_folder):
    """Extract all images from a PDF, named by section context."""
    product_dir = os.path.join(EXTRACTED_DIR, product_folder)

    # Clean existing files
    if os.path.exists(product_dir):
        for f in os.listdir(product_dir):
            fp = os.path.join(product_dir, f)
            if os.path.isfile(fp) and not f.endswith('.json'):
                os.remove(fp)
    shadow_dir = os.path.join(product_dir, "shadowed")
    if os.path.exists(shadow_dir):
        for f in os.listdir(shadow_dir):
            os.remove(os.path.join(shadow_dir, f))
    os.makedirs(shadow_dir, exist_ok=True)
    os.makedirs(product_dir, exist_ok=True)

    doc = fitz.open(pdf_path)

    # Step 1: Find all unique image xrefs
    all_xrefs = set()
    for page in doc:
        for img in page.get_images(full=True):
            all_xrefs.add(img[0])

    # Step 2: For each xref, determine which page it actually appears on
    xref_to_page = {}
    for xref in all_xrefs:
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            rects = page.get_image_rects(xref)
            if rects:
                xref_to_page[xref] = page_idx
                break  # first page where it appears

    # Step 3: Determine section for each page
    page_sections = {}
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        if page_idx == 0:
            section = "cover"
        elif page_idx == 1:
            section = "produktbilder"
        else:
            detected = detect_section_for_page(page)
            section = detected or f"seite{page_idx + 1}"
        page_sections[page_idx] = section

    # Step 4: Extract images, sorted by page then xref
    xrefs_by_page = defaultdict(list)
    for xref, page_idx in xref_to_page.items():
        xrefs_by_page[page_idx].append(xref)

    section_counts = defaultdict(int)
    extracted = []

    for page_idx in sorted(xrefs_by_page.keys()):
        section = page_sections.get(page_idx, f"seite{page_idx + 1}")
        xrefs = sorted(xrefs_by_page[page_idx])

        for xref in xrefs:
            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue
            if not base_image or len(base_image["image"]) < MIN_IMAGE_SIZE:
                continue

            image_bytes = base_image["image"]
            ext = base_image.get("ext", "png")
            if ext == "jpeg":
                ext = "jpg"

            # Generate descriptive name
            section_counts[section] += 1
            count = section_counts[section]
            if count > 1:
                name = f"{product_folder}_{section}_{count}.{ext}"
            else:
                name = f"{product_folder}_{section}.{ext}"

            out_path = os.path.join(product_dir, name)
            with open(out_path, 'wb') as f:
                f.write(image_bytes)
            extracted.append(name)

    doc.close()

    # Step 5: Generate shadows
    shadow_count = 0
    for fname in extracted:
        src = os.path.join(product_dir, fname)
        base = os.path.splitext(fname)[0]
        dst = os.path.join(shadow_dir, f"shadow_{base}.jpg")
        if create_shadow(src, dst):
            shadow_count += 1

    return extracted, shadow_count


def main():
    print("=" * 70)
    print("Extract ALL images with descriptive section-based names")
    print("=" * 70)

    all_files = os.listdir(MECAL_DIR)
    pdf_files = sorted([f for f in all_files if f.lower().endswith('.pdf')])

    total_images = 0
    total_shadows = 0
    total_products = 0

    for fname in pdf_files:
        folder = filename_to_folder(fname)
        if folder is None:
            continue
        if folder in SKIP_PRODUCTS:
            print(f"  SKIP {folder} (already configured)")
            continue

        pdf_path = os.path.join(MECAL_DIR, fname)
        # Check for duplicate PDFs mapping to same folder
        product_dir = os.path.join(EXTRACTED_DIR, folder)
        if os.path.exists(product_dir):
            existing = [f for f in os.listdir(product_dir)
                        if os.path.isfile(os.path.join(product_dir, f))
                        and not f.endswith('.json') and not f.startswith('_')]
            # If already has section-named files (not _cover_N), skip
            if existing and not all('_cover' in f or '_seite' in f for f in existing[:3]):
                # Check if names are descriptive (not just sequential)
                has_descriptive = any(
                    any(s in f for s in ['hauptansichten', 'elektrospindel', 'beschreibung',
                                          'umfangsschutz', 'saegediagramm', 'produktbilder',
                                          'kuehlung', 'rollenbahn', 'sicherheit'])
                    for f in existing
                )
                if has_descriptive:
                    print(f"  SKIP {folder} (already has descriptive names)")
                    continue

        print(f"  {folder}...", end=" ", flush=True)
        try:
            extracted, shadow_count = extract_product_from_pdf(pdf_path, folder)
            total_images += len(extracted)
            total_shadows += shadow_count
            total_products += 1
            print(f"{len(extracted)} images, {shadow_count} shadows")
        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\n{'=' * 70}")
    print(f"  Products processed: {total_products}")
    print(f"  Total images:       {total_images}")
    print(f"  Total shadows:      {total_shadows}")


if __name__ == "__main__":
    main()
