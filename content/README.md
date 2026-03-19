# content/

This folder is where you place your product documents, images, and data for processing via the Rattle API.

## Suggested structure

```
content/
  <tenant>/
    documents/    # DOCX, PDF product data sheets
    images/       # Product photos, extracted images
    data/         # Excel spreadsheets, CSV files, JSON
```

For example:
```
content/
  acme/
    documents/widget-pro-datasheet.pdf
    images/widget-pro-front.jpg
    data/widget-pro-options.xlsx
```

## This folder is gitignored

The `content/` directory is listed in `.gitignore` (except for this README). Your proprietary product data stays local and is never committed to version control.

## Discovering content files

AI agents and scripts can discover and process files placed here using `source_reader.py` from the project root. The `list_sources()` function walks a tenant directory and returns all files:

```python
from source_reader import list_sources

# List all files for a tenant
files = list_sources("acme")
# -> ['documents/widget-pro-datasheet.pdf', 'images/widget-pro-front.jpg', ...]
```

## Referencing content files in scripts

```python
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content", "acme")

# Reference a specific image
image_path = os.path.join(CONTENT_DIR, "images", "widget-pro-front.jpg")

# Reference a document
doc_path = os.path.join(CONTENT_DIR, "documents", "widget-pro-datasheet.pdf")
```
