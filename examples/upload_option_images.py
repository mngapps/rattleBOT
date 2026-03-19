"""
Example: Upload option images with automatic shadow generation.

Demonstrates how to:
  - Define option groups with the mit/ohne (with/without) pattern
  - Use upload_option_images() from image_utils for declarative uploads
  - Automatically generate greyed-out images for 'ohne' (without) options

The mit/ohne pattern:
  - 'mit' (with) options get the real product image
  - 'ohne' (without) options get an auto-generated greyed-out/shadowed
    version of the same image (50% opacity, desaturated)

Usage:
    python examples/upload_option_images.py

Before running:
  - Replace TENANT with your tenant name
  - Replace option IDs with your actual Rattle option IDs
  - Replace image filenames with your actual image files
  - Update IMG_DIR to point to your image directory
"""

import os
import sys

# Add project root to path so we can import client, image_utils, etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from client import RattleClient
from image_utils import upload_option_images

# ---------------------------------------------------------------------------
# Configuration — replace these with your actual values
# ---------------------------------------------------------------------------
TENANT = "your_tenant"

# Directory containing your option images
IMG_DIR = os.path.join(
    os.path.dirname(__file__), "..", "content", TENANT, "images", "my_product"
)

client = RattleClient(TENANT)

# ---------------------------------------------------------------------------
# Option group definitions
# ---------------------------------------------------------------------------
# Each group is a dict with:
#   "name"    - display name for logging (not sent to API)
#   "options" - list of option dicts:
#       "id"    - Rattle option ID (required)
#       "label" - human-readable label for logging (required)
#       "image" - filename in IMG_DIR (required unless ohne=True)
#       "ohne"  - if True, a shadowed version of the group's last real
#                 image will be auto-generated and uploaded (optional)
#
# Find your option IDs via: client.get("products/<id>") or in the Rattle UI.

OPTION_GROUPS = [
    # --- Group: Model variants ---
    # All options in this group share images; no ohne/mit pattern needed.
    {
        "name": "Model Variant",
        "options": [
            {"id": 1001, "label": "Model A - Standard",  "image": "model_a.jpg"},
            {"id": 1002, "label": "Model A - Extended",   "image": "model_a.jpg"},
            {"id": 1003, "label": "Model B - Compact",    "image": "model_b.jpg"},
        ],
    },

    # --- Group: Optional upgrade (mit/ohne pattern) ---
    # The 'mit' option gets the real image. The 'ohne' option gets a
    # greyed-out version generated automatically by image_utils.
    {
        "name": "Reinforced Spindle",
        "options": [
            {"id": 2001, "label": "mit",  "image": "spindle_upgrade.jpg"},
            {"id": 2002, "label": "ohne", "ohne": True},
        ],
    },

    # --- Group: Accessories (all have distinct images) ---
    {
        "name": "Accessories",
        "options": [
            {"id": 3001, "label": "Tool holder A",    "image": "tool_holder_a.jpg"},
            {"id": 3002, "label": "Tool holder B",    "image": "tool_holder_b.jpg"},
            {"id": 3003, "label": "Chip conveyor",    "image": "chip_conveyor.jpg"},
        ],
    },

    # --- Group: Software add-on (mit/ohne pattern) ---
    {
        "name": "CAM Software Package",
        "options": [
            {"id": 4001, "label": "mit",  "image": "cam_software.jpg"},
            {"id": 4002, "label": "ohne", "ohne": True},
        ],
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Uploading option images")
    print("=" * 60)

    upload_option_images(client, IMG_DIR, OPTION_GROUPS)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
