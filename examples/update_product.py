"""
Example: Full product update workflow.

Demonstrates how to:
  1. Upload gallery images to a product
  2. Upload content images to an area (for embedding in rich text)
  3. Build EditorJS rich text blocks (paragraph, header, table, image, list)
  4. Update area description and content

Usage:
    python examples/update_product.py

Before running:
  - Replace PRODUCT_ID, AREA_ID with your actual Rattle resource IDs
  - Replace TENANT with your tenant name
  - Place your images in IMG_DIR (e.g. content/<tenant>/images/<product>/)
"""

import os
import sys

# Add project root to path so we can import client, image_utils, etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from client import RattleClient

# ---------------------------------------------------------------------------
# Configuration — replace these with your actual values
# ---------------------------------------------------------------------------
TENANT = "your_tenant"          # Your tenant slug
PRODUCT_ID = 1                  # Product ID from Rattle
AREA_ID = 100                   # Area ID associated with the product

# Directory containing your product images
IMG_DIR = os.path.join(
    os.path.dirname(__file__), "..", "content", TENANT, "images", "my_product"
)

client = RattleClient(TENANT)


# ---------------------------------------------------------------------------
# Step 1: Upload gallery images
# ---------------------------------------------------------------------------
def upload_gallery_images():
    """Upload product photos to the product gallery.

    Each entry is a (filename, alt_text) tuple. The images appear in the
    product's image carousel in the order they are uploaded.
    """
    gallery_images = [
        # (filename, description/alt text)
        ("product_front.jpg", "Product front view"),
        ("product_side.jpg", "Product side view"),
        ("product_detail.jpg", "Close-up detail shot"),
    ]

    uploaded = []
    for filename, desc in gallery_images:
        filepath = os.path.join(IMG_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP (not found): {filename}")
            continue
        try:
            result = client.upload_image(f"products/{PRODUCT_ID}/gallery", filepath)
            img_data = result.get("data", result)
            print(f"  OK gallery: {filename} -> id={img_data.get('id')}")
            uploaded.append(img_data)
        except Exception as e:
            print(f"  FAIL gallery: {filename}: {e}")
    return uploaded


# ---------------------------------------------------------------------------
# Step 2: Upload content images (for embedding in rich text)
# ---------------------------------------------------------------------------
def upload_content_images():
    """Upload images for embedding in area rich text content.

    These are uploaded to the area's content image store. The returned URLs
    are then referenced in EditorJS image blocks.
    """
    content_images = [
        "product_front.jpg",       # Hero image for the content header
        "product_specs_chart.jpg", # Specs chart or datasheet image
        "product_detail.jpg",      # Detail photo for inline use
    ]

    uploaded = {}
    for filename in content_images:
        filepath = os.path.join(IMG_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP content img (not found): {filename}")
            continue
        try:
            result = client.upload_image(f"areas/{AREA_ID}/content/images", filepath)
            img_data = result.get("data", result)
            uploaded[filename] = img_data
            print(f"  OK content image: {filename} -> {img_data.get('url', img_data.get('file', {}).get('url', '?'))}")
        except Exception as e:
            print(f"  FAIL content image: {filename}: {e}")
    return uploaded


# ---------------------------------------------------------------------------
# Step 3: Build EditorJS rich text blocks
# ---------------------------------------------------------------------------
def build_content_blocks(content_images):
    """Build the EditorJS block list for the area content.

    Demonstrates all common block types: image, paragraph, header, list, table.
    Each block needs a unique 'id', a 'type', and a 'data' dict.
    """

    def img_url(filename):
        """Helper to get the uploaded URL for a content image."""
        data = content_images.get(filename, {})
        return data.get("url", data.get("file", {}).get("url", ""))

    blocks = [
        # --- Hero image ---
        {
            "id": "hero_img",
            "type": "image",
            "data": {
                "file": {"url": img_url("product_front.jpg")},
                "caption": "Product overview",
                "withBorder": False,
                "withBackground": False,
                "stretched": True,
            },
        },

        # --- Introductory paragraph ---
        # Use <b> for bold, <i> for italic, <a href="..."> for links.
        {
            "id": "intro_paragraph",
            "type": "paragraph",
            "data": {
                "text": (
                    "<b>Product Name</b> — A short introductory paragraph "
                    "describing what this product is and its key value proposition."
                ),
            },
        },

        # --- Section header ---
        # level: 1-6 (typically 3 for section headers within content)
        {
            "id": "specs_header",
            "type": "header",
            "data": {"text": "Technical Specifications", "level": 3},
        },

        # --- Specifications table ---
        # withHeadings: True means the first row is treated as a header row.
        # stretched: True makes the table full-width.
        {
            "id": "specs_table",
            "type": "table",
            "data": {
                "withHeadings": True,
                "stretched": True,
                "content": [
                    ["Property", "Unit", "Value"],
                    ["Width", "mm", "1200"],
                    ["Height", "mm", "800"],
                    ["Weight", "kg", "150"],
                    ["Power", "kW", "5.5"],
                ],
            },
        },

        # --- Inline image with caption ---
        {
            "id": "specs_chart_img",
            "type": "image",
            "data": {
                "file": {"url": img_url("product_specs_chart.jpg")},
                "caption": "Performance chart — load vs. speed",
                "withBorder": False,
                "withBackground": False,
                "stretched": False,
            },
        },

        # --- Features header ---
        {
            "id": "features_header",
            "type": "header",
            "data": {"text": "Key Features", "level": 3},
        },

        # --- Unordered list ---
        # Each item has 'content' (HTML string), 'items' (nested list), 'meta'.
        {
            "id": "features_list",
            "type": "list",
            "data": {
                "style": "unordered",
                "meta": {},
                "items": [
                    {"content": "High-precision machining with 4 NC-controlled axes", "items": [], "meta": {}},
                    {"content": "Automatic tool changer with 8-slot magazine", "items": [], "meta": {}},
                    {"content": "Integrated safety enclosure with optical barriers", "items": [], "meta": {}},
                    {"content": "Compatible with standard ISO30 and optional HSK-63F tooling", "items": [], "meta": {}},
                ],
            },
        },

        # --- Another section with a detail image ---
        {
            "id": "detail_header",
            "type": "header",
            "data": {"text": "Design Details", "level": 3},
        },
        {
            "id": "detail_paragraph",
            "type": "paragraph",
            "data": {
                "text": (
                    "The modular design allows for flexible configuration. "
                    "All guides and ball screws are lubricated via an automatic "
                    "central lubrication system."
                ),
            },
        },
        {
            "id": "detail_img",
            "type": "image",
            "data": {
                "file": {"url": img_url("product_detail.jpg")},
                "caption": "Detail view — modular component assembly",
                "withBorder": False,
                "withBackground": False,
                "stretched": False,
            },
        },

        # --- Footer note ---
        {
            "id": "footer_note",
            "type": "paragraph",
            "data": {
                "text": "<i>All specifications subject to change. Contact us for the latest data.</i>",
            },
        },
    ]

    # Filter out image blocks where the upload failed (no URL available)
    filtered = []
    for block in blocks:
        if block["type"] == "image":
            url = block["data"].get("file", {}).get("url", "")
            if not url:
                print(f"  Skipping image block {block['id']} (no URL)")
                continue
        filtered.append(block)

    return filtered


# ---------------------------------------------------------------------------
# Step 4: Update area description and content
# ---------------------------------------------------------------------------
def update_area_description():
    """Update the area's short description (plain text)."""
    description = (
        "A short, plain-text summary of this product. "
        "This appears in search results and area listings."
    )
    try:
        result = client.patch(f"areas/{AREA_ID}", json={"description": description})
        print("  OK area description updated")
        return result
    except Exception as e:
        print(f"  FAIL area description: {e}")
        return None


def update_area_content(blocks):
    """Update the area's rich text content (EditorJS format)."""
    payload = {
        "blocks": blocks,
        "enabled": True,
        "language": "EN",     # Language code for the content
    }
    try:
        result = client.put(f"areas/{AREA_ID}/content", json=payload)
        print(f"  OK area content updated ({len(blocks)} blocks)")
        return result
    except Exception as e:
        print(f"  FAIL area content: {e}")
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print(f"Updating Product {PRODUCT_ID}, Area {AREA_ID}")
    print("=" * 60)

    # 1. Upload gallery images
    print("\n[1/4] Uploading gallery images...")
    gallery = upload_gallery_images()
    print(f"  Total gallery images uploaded: {len(gallery)}")

    # 2. Upload content images for embedding
    print("\n[2/4] Uploading content images...")
    content_images = upload_content_images()
    print(f"  Total content images uploaded: {len(content_images)}")

    # 3. Update area description
    print("\n[3/4] Updating area description...")
    update_area_description()

    # 4. Build and update area content (rich text)
    print("\n[4/4] Updating area content (rich text)...")
    blocks = build_content_blocks(content_images)
    update_area_content(blocks)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
