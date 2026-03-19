# Rattle API — Agent Primer

This document is for AI agents working with the Rattle API. Read this before generating any code or content. It explains what you're building, how the data model works, and the patterns that produce good results.

## Before You Start — REQUIRED

**You must read the latest API reference before writing any API calls.** The endpoint examples in this document are illustrative — the live docs are the only source of truth for endpoints, fields, and response shapes.

### Option A: Read the local reference (preferred)

If `api_reference/` exists, read these files first:
- `api_reference/endpoints.md` — human-readable list of all endpoints, grouped by resource, with parameters
- `api_reference/openapi.json` — full OpenAPI spec with request/response schemas
- `api_reference/meta.json` — check `fetched_at` to see how fresh the docs are

If the folder is missing or stale, run:
```bash
python3 tools/fetch_api_docs.py
```

### Option B: Fetch live docs directly

If you have web access, fetch from these URLs:
- **OpenAPI spec**: https://www.rattleapp.de/api/v1/openapi.json
- **Developer guide**: https://www.rattleapp.de/api/v1/developers
- **Interactive docs**: https://www.rattleapp.de/api/v1/docs

### Why this matters

The Rattle API evolves. Endpoints get added, fields get renamed, new features ship. Code generated against stale docs will break. Always verify against the live reference.

## What is Rattle?

Rattle is a **CPQ (Configure, Price, Quote) platform**. Manufacturers use it to present complex industrial products (machinery, equipment, systems) where customers choose from many options and variants. Think of it as a structured product catalog with interactive configuration and quoting.

The Rattle API (`https://www.rattleapp.de/api/v1`) lets you programmatically manage all configurator content: products, areas, option groups, images, rich text, pricing, customers, quotes, and documents.

## Data Model

The core configurator hierarchy:

```
Tenant
  └── Products
        ├── Gallery Images          (product photos for the carousel)
        ├── Price Overrides         (custom pricing rules)
        ├── Pricing Presets         (surcharges, discounts, fees)
        └── Areas
              ├── Description        (plain text summary)
              ├── Content            (rich text in EditorJS format)
              ├── Content Images     (uploaded separately, referenced in content)
              ├── Price Overrides
              └── Option Groups
                    └── Options
                          └── Option Image
```

Beyond the configurator, the API also covers: Customers, Opportunities, Quotes, Line Items, Documents, Configurations, Parts/BOM, Connectors, Webhooks, and Change Management (branches, change requests, approvals).

### Products

A product is a configurable item — typically an industrial machine or system. Each product has a gallery (image carousel), pricing, and one or more areas.

### Areas

An area is a content section within a product. It has a plain-text **description** (shown in search/listings) and **rich text content** (the detailed technical page). Areas also hold the option groups. Areas can exist in a library (unassigned) or be assigned to products.

### Option Groups and Options

Option groups represent configurable aspects of a product (e.g., "Spindle Type", "Software Package", "Accessories"). Each group contains options that the customer can select. Options have IDs, labels, pricing, and optional images.

## API Conventions

These conventions apply across all endpoints:

- **Authentication**: Bearer token in the Authorization header: `Authorization: Bearer rk_live_...`
- **Response envelope**: All responses return `{ "data": ..., "meta": ..., "links": ... }`
- **Pagination**: Cursor-based. Default 25 items, max 100. Use `?per_page=N` and follow `meta.next_cursor`
- **Errors**: RFC 9457 Problem Details format with field-level validation errors
- **Rate limiting**: Check `X-RateLimit-*` headers. On 429, respect `Retry-After`
- **ETags**: Use `If-Match` for safe updates, `If-None-Match` for conditional reads
- **Idempotency**: Include `X-Idempotency-Key` on mutating requests to prevent duplicates
- **Field selection**: `?fields=name,price` to reduce payload size
- **Expansion**: `?expand=areas,groups` to embed related resources inline
- **Sorting**: `?sort=name` (ascending) or `?sort=-created_at` (descending)
- **Batch operations**: `POST /batch` for up to 100 operations in one request
- **Max request body**: 1 MB
- **Timeout**: 60 seconds

## Rich Text Content (EditorJS)

Area content uses the [EditorJS](https://editorjs.io/) block format. Each block has:

```json
{
    "id": "unique_string",
    "type": "paragraph|header|table|image|list|quote|code",
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

API keys are created in the Rattle web dashboard under Settings > Connectors > API Keys. Each key has configurable permission scopes (products read/write, pricing, customers, quotes, etc.).

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

- **Check the live API docs first.** Endpoints and fields may have changed since this document was written. Fetch https://www.rattleapp.de/api/v1/developers or the OpenAPI spec before writing API calls.
- **Block IDs must be unique** within a content update. Use descriptive prefixes: `sec_specs_h`, `sec_specs_tbl`, `detail_img_01`.
- **Tables are the primary format for technical specs.** Prefer tables over paragraphs for anything with units and values.
- **Use inline HTML sparingly** in paragraphs. Bold for emphasis, italic for notes, that's it.
- **Always filter out image blocks with empty URLs** before sending the content update — an upload might fail and you don't want broken image blocks.
- **One area = one product variant's full technical description.** Don't split a product across multiple areas unless the API structure requires it.
- **Option images should be product-contextual.** Show the actual component/feature being configured, not a generic icon.
- **Use `?expand=` to reduce round-trips.** For example, `GET products/{id}?expand=areas,groups` returns everything in one call.
- **Use ETags for safe updates.** When updating content that others may be editing, include `If-Match` to avoid overwriting changes.
