# Rattle API

Python client for the [Rattle REST API](https://www.rattleapp.de/api/v1). Manage products, areas, options, images, and rich text content programmatically.

## Quick Start

```bash
git clone https://github.com/<your-username>/rattle-api.git
cd rattle-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your API key:

```bash
cp .env.example .env
```

```env
RATTLE_API_KEY_MYTENANT=rk_live_your_key_here
```

Verify your connection:

```bash
python main.py mytenant test-connection
```

## Usage

```python
from client import RattleClient

client = RattleClient("mytenant")

# List products
products = client.list_all("products")

# Get a single product
product = client.get("products/42")

# Create a product
client.post("products", json={"name": "New Product"})

# Update a product
client.patch("products/42", json={"name": "Updated Name"})

# Delete a product
client.delete("products/42")

# Upload an image to a product gallery
client.upload_image("products/42/gallery", "path/to/image.jpg")

# Upload an image for area content embedding
client.upload_image("areas/100/content/images", "path/to/image.jpg")

# Paginated listing (automatic cursor handling)
all_items = client.list_all("products", per_page=50)
```

## Multi-Tenant Support

Configure multiple tenants via environment variables:

```env
RATTLE_API_KEY_TENANT1=rk_live_...
RATTLE_API_KEY_TENANT2=rk_live_...
```

Each `RATTLE_API_KEY_<NAME>` becomes a tenant you can reference by name:

```python
client_a = RattleClient("tenant1")
client_b = RattleClient("tenant2")
```

## CLI

```bash
# Test API connection
python main.py <tenant> test-connection

# List content files for a tenant
python main.py <tenant> list-content
```

## Content Folder

The `content/` directory is where you place your product documents, images, and data files. It is gitignored so your proprietary data stays local.

Suggested structure:

```
content/
  mytenant/
    documents/    # DOCX, PDF source files
    images/       # Product photos, extracted images
    data/         # Excel sheets, CSV files
```

The `source_reader.py` module discovers files in this folder automatically. AI agents can use this as a standardized location to find and process content for Rattle uploads.

See `content/README.md` for details.

## Utilities

### image_utils.py

Image manipulation for option management:

- `create_shadowed_image(src, dst)` — Generate a greyed-out "ohne" (without) version of an image
- `upload_option_images(client, img_dir, option_groups)` — Upload option images with automatic shadow generation for mit/ohne patterns

Requires `Pillow` (`pip install Pillow`).

### source_reader.py

Content file discovery and data reading:

- `list_sources(tenant)` — List all content files for a tenant
- `read_excel(filepath)` — Read an Excel file into a list of dicts

Requires `openpyxl` for Excel support.

## Examples

See the `examples/` folder for working templates:

| Script | Description |
|--------|-------------|
| `update_product.py` | Full workflow: gallery upload, content images, EditorJS rich text |
| `upload_option_images.py` | Option group images with automatic shadow generation |
| `extract_images.py` | Extract images from DOCX and PDF files |

## API Reference

This client wraps the Rattle REST API at `https://www.rattleapp.de/api/v1`. Refer to your Rattle account documentation for available endpoints and data schemas.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
