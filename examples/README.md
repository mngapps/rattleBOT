# examples/

Example scripts demonstrating common Rattle API workflows. Each script is a self-contained template you can copy and adapt for your own products.

## Scripts

### update_product.py

Full product update workflow covering:
- Setting up `RattleClient` with a tenant
- Uploading gallery images to a product
- Uploading content images to an area
- Building EditorJS rich text blocks (paragraph, header, table, image, list)
- Updating area description and content

### upload_option_images.py

Option group image upload with automatic shadow generation:
- Defining option groups with the mit/ohne (with/without) pattern
- Using `upload_option_images()` from `image_utils` to handle uploads
- Automatic generation of greyed-out images for "ohne" (without) options

### extract_images.py

Extract images from DOCX and PDF files:
- `extract_from_docx()`: extracts images from DOCX using `zipfile`
- `extract_from_pdf()`: extracts images from PDF using PyMuPDF (`fitz`)
- CLI usage with `argparse` for specifying input file and output directory

## Adapting examples to your own products

1. **Copy** the example script you need into your working area or edit it directly.
2. **Replace placeholder IDs** (`PRODUCT_ID`, `AREA_ID`, option IDs) with your actual Rattle resource IDs. You can find these in the Rattle control panel or via `client.get("products")`.
3. **Update the tenant name** in the `RattleClient("your_tenant")` call.
4. **Point to your images** by updating `IMG_DIR` to your `content/<tenant>/images/` directory.
5. **Customize the content blocks** in `build_content_blocks()` with your product's actual text, tables, and image references.
6. **Run the script** from the project root or the `examples/` directory:
   ```bash
   python examples/update_product.py
   ```
