# Rattle API

Python client for the [Rattle REST API](https://www.rattleapp.de/api/v1). Manage products, areas, options, images, and rich text content programmatically.

## Setup

```bash
git clone https://github.com/<your-username>/rattle-api.git
cd rattle-api
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create your `.env` file with your Rattle API key:

```bash
cp .env.example .env
```

Edit `.env` and replace the placeholder:

```env
RATTLE_API_KEY_MYTENANT=rk_live_your_key_here
```

The name after `RATTLE_API_KEY_` becomes your tenant name (case-insensitive). Add multiple lines for multiple tenants.

Test your connection:

```bash
python3 main.py mytenant test-connection
```

Fetch the latest API docs (used by tools and AI agents):

```bash
python3 tools/fetch_api_docs.py
```

This downloads the OpenAPI spec and developer guide into `api_reference/` (gitignored). Re-run anytime to refresh.

### Optional dependencies

The core client only needs `requests` and `python-dotenv`. Install extras as needed:

```bash
pip install Pillow          # Image manipulation (image_utils.py)
pip install openpyxl        # Excel reading (source_reader.py)
pip install PyMuPDF         # PDF extraction (tools/, examples/)
pip install python-docx     # DOCX extraction (tools/)
```

Or install everything at once:

```bash
pip install Pillow openpyxl PyMuPDF python-docx
```

## Project Structure

```
rattle-api/
├── client.py              # RattleClient — core API wrapper
├── config.py              # Multi-tenant config (reads .env automatically)
├── main.py                # CLI entry point
├── source_reader.py       # Content file discovery + Excel reader
├── image_utils.py         # Image manipulation for option uploads
├── tools/
│   └── extract_content.py # Extract text/tables from PDF, DOCX, XLSX
├── examples/              # Workflow templates (copy and adapt)
│   ├── update_product.py
│   ├── upload_option_images.py
│   └── extract_images.py
├── content/               # Your data goes here (gitignored)
│   └── README.md
├── .env.example           # API key template
├── AGENTS.md              # Data model primer for AI agents
└── pyproject.toml
```

## Usage

```python
from client import RattleClient

client = RattleClient("mytenant")

# List all products (handles pagination automatically)
products = client.list_all("products")

# Get a single product
product = client.get("products/42")

# Create
client.post("products", json={"name": "New Product"})

# Update
client.patch("products/42", json={"name": "Updated Name"})

# Delete
client.delete("products/42")

# Upload an image to a product gallery
client.upload_image("products/42/gallery", "photo.jpg")

# Upload a content image (for embedding in rich text)
result = client.upload_image("areas/100/content/images", "diagram.jpg")
url = result["data"]["file"]["url"]
```

## CLI

```bash
python3 main.py <tenant> test-connection   # Verify API access
python3 main.py <tenant> list-content      # List content files for a tenant
```

## Content Folder

Place your product documents, images, and data in `content/`. This folder is gitignored so proprietary data stays local.

```
content/
  mytenant/
    documents/    # DOCX, PDF source files
    images/       # Product photos
    data/         # Excel sheets, CSV files
```

Scripts and AI agents discover files here automatically via `source_reader.list_sources("mytenant")`.

## Tools

### Extract content from documents

Pull structured text, headings, and tables from source documents:

```bash
# PDF → normalized JSON
python3 tools/extract_content.py datasheet.pdf

# DOCX → EditorJS blocks (ready for the Rattle API)
python3 tools/extract_content.py datasheet.docx --format editorjs

# Excel sheet
python3 tools/extract_content.py specs.xlsx --sheet "Specs"

# Save to file
python3 tools/extract_content.py datasheet.pdf --format editorjs -o blocks.json
```

### Extract images from documents

```bash
python3 examples/extract_images.py datasheet.pdf -o images/
python3 examples/extract_images.py document.docx --min-size 10000
```

## Examples

The `examples/` folder contains workflow templates you can copy and adapt:

| Script | What it demonstrates |
|--------|---------------------|
| `update_product.py` | Gallery upload, content images, EditorJS rich text blocks |
| `upload_option_images.py` | Option group image uploads with shadow generation |
| `extract_images.py` | Image extraction from DOCX and PDF files |

See `examples/README.md` for how to adapt them to your products.

## For AI Agents

See [AGENTS.md](AGENTS.md) for a primer on the Rattle data model, EditorJS block format, and content conventions. Point your agent at this file before it starts generating configurator content.

## API Documentation

- [Developer guide](https://www.rattleapp.de/api/v1/developers) — concepts, authentication, pagination, error handling
- [Interactive docs (Swagger UI)](https://www.rattleapp.de/api/v1/docs) — try endpoints, see request/response schemas
- [OpenAPI spec](https://www.rattleapp.de/api/v1/openapi.json) — machine-readable endpoint and schema reference

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
