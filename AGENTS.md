# Rattle API — Agent Primer

This document is for AI agents working with the Rattle API. Read this before generating any code or content. It explains what you're building, how the data model works, and the patterns that produce good results.

## What is Rattle?

Rattle is a **product configurator platform**. Manufacturers use it to present complex industrial products (machinery, equipment, systems) where customers choose from many options and variants. Think of it as a structured product catalog with interactive configuration.

The Rattle API (`https://www.rattleapp.de/api/v1`) lets you programmatically manage all configurator content: products, technical descriptions, option groups, images, and rich text.

## Data Model

The hierarchy is:

```
Tenant
  └── Products
        ├── Gallery Images          (product photos for the carousel)
        └── Areas
              ├── Description        (plain text summary)
              ├── Content            (rich text in EditorJS format)
              ├── Content Images     (uploaded separately, referenced in content)
              └── Option Groups
                    └── Options
                          └── Option Image
```

### Products

A product is a configurable item — typically an industrial machine or system. Each product has a gallery (image carousel) and one or more areas.

- `GET products` — list all products (paginated)
- `GET products/{id}` — get a single product with its areas and option groups
- `POST products/{id}/gallery` — upload a gallery image (multipart file upload)

### Areas

An area is a content section within a product. It has a plain-text **description** (shown in search/listings) and **rich text content** (the detailed technical page). Areas also hold the option groups.

- `PATCH areas/{id}` — update area description (`{"description": "..."}`)
- `PUT areas/{id}/content` — replace area rich text content
- `POST areas/{id}/content/images` — upload an image for embedding in content

### Option Groups and Options

Option groups represent configurable aspects of a product (e.g., "Spindle Type", "Software Package", "Accessories"). Each group contains options that the customer can select.

- Options have IDs, labels, and optional images
- `POST options/{id}/image` — upload an option's image

## Rich Text Content (EditorJS)

Area content uses the [EditorJS](https://editorjs.io/) block format. Each block has:

```json
{
    "id": "unique_string",
    "type": "paragraph|header|table|image|list",
    "data": { ... }
}
```

The content is sent as:

```json
{
    "blocks": [ ... ],
    "enabled": true,
    "language": "DE"
}
```

### Block Types

**Paragraph** — body text, supports inline HTML (`<b>`, `<i>`, `<a>`):
```json
{
    "id": "intro_01",
    "type": "paragraph",
    "data": {
        "text": "<b>Product Name</b> — description of the product."
    }
}
```

**Header** — section heading, level 1-6 (use 3 for main sections):
```json
{
    "id": "section_heading",
    "type": "header",
    "data": {"text": "Technical Specifications", "level": 3}
}
```

**Table** — specification tables are very common in product content:
```json
{
    "id": "specs_table",
    "type": "table",
    "data": {
        "withHeadings": true,
        "stretched": true,
        "content": [
            ["Property", "Unit", "Value"],
            ["Power", "kW", "6.0"],
            ["Speed", "rpm", "18000"]
        ]
    }
}
```

**Image** — uploaded content images, referenced by URL:
```json
{
    "id": "detail_photo",
    "type": "image",
    "data": {
        "file": {"url": "https://...uploaded_url..."},
        "caption": "Detail view — component assembly",
        "withBorder": false,
        "withBackground": false,
        "stretched": false
    }
}
```

**List** — feature lists, unordered or ordered:
```json
{
    "id": "features_list",
    "type": "list",
    "data": {
        "style": "unordered",
        "meta": {},
        "items": [
            {"content": "Feature one description", "items": [], "meta": {}},
            {"content": "Feature two description", "items": [], "meta": {}}
        ]
    }
}
```

### Content Image Workflow

Images in rich text content require a two-step process:

1. **Upload** the image to the area's content image store:
   ```python
   result = client.upload_image(f"areas/{AREA_ID}/content/images", filepath)
   url = result["data"]["url"]  # or result["data"]["file"]["url"]
   ```

2. **Reference** the returned URL in an image block:
   ```python
   {"type": "image", "data": {"file": {"url": url}, ...}}
   ```

Gallery images (product carousel) are uploaded separately to `products/{id}/gallery` and are *not* used in content blocks.

## Content Structure Patterns

When building product content from source documents, follow this structure:

1. **Hero image** — stretched, full-width product photo at the top
2. **Introduction** — 1-2 paragraph summary with key specs bolded
3. **Technical sections** — each with a level-3 header, followed by:
   - A spec table (Property / Unit / Value) for quantitative data
   - A bullet list for qualitative features
   - Inline images for diagrams, charts, or detail photos
4. **Footer** — legend explaining status symbols (if used)

### Status Symbols Convention

In specification tables:
- `●` = Standard (included by default)
- `□` = Optional (available at extra cost)
- `n.d.` = Not defined / not available

## Working with Content Files

Users place their source documents in the `content/` folder:

```
content/<tenant>/documents/   — PDF and DOCX source files
content/<tenant>/images/      — extracted or provided images
content/<tenant>/data/        — Excel files with structured data
```

Use `tools/extract_content.py` to extract structured text and tables from these documents, then convert the output into EditorJS blocks.

Use `source_reader.py` to discover files:
```python
from source_reader import list_sources, read_excel
files = list_sources("tenant_name")
data = read_excel("content/tenant/data/specs.xlsx")
```

## API Authentication

Each tenant has its own API key, set via environment variables:

```
RATTLE_API_KEY_TENANTNAME=rk_live_...
```

The `RattleClient` reads these automatically:

```python
from client import RattleClient
client = RattleClient("tenantname")
```

## Common Workflow

A typical product setup script follows these steps:

1. **Extract content** from source documents (PDF/DOCX) using `tools/extract_content.py`
2. **Extract images** from source documents using `examples/extract_images.py`
3. **Upload gallery images** to `products/{id}/gallery`
4. **Upload content images** to `areas/{id}/content/images` and collect the returned URLs
5. **Build EditorJS blocks** using the extracted text and uploaded image URLs
6. **Update area description** via `PATCH areas/{id}`
7. **Update area content** via `PUT areas/{id}/content`
8. **Upload option images** using `image_utils.upload_option_images()`

## Tips for Good Output

- **Block IDs must be unique** within a content update. Use descriptive prefixes: `sec_specs_h`, `sec_specs_tbl`, `detail_img_01`.
- **Tables are the primary format for technical specs.** Prefer tables over paragraphs for anything with units and values.
- **Use inline HTML sparingly** in paragraphs. Bold for emphasis, italic for notes, that's it.
- **Always filter out image blocks with empty URLs** before sending the content update — an upload might fail and you don't want broken image blocks.
- **One area = one product variant's full technical description.** Don't split a product across multiple areas unless the API structure requires it.
- **Option images should be product-contextual.** Show the actual component/feature being configured, not a generic icon.
