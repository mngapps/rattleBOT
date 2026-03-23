"""
Shared image utilities for Rattle option image management.

Provides:
  - create_shadowed_image(): generate a greyed-out "ohne" version of an image
  - upload_option_images(): declarative option-group upload with automatic
    shadow generation for 'ohne' entries
"""

import os

from PIL import Image, ImageEnhance


def create_shadowed_image(src_path, dst_path):
    """Create a greyed-out / shadowed version of an image.

    Used for 'ohne' (without) options — takes the 'mit' (with) image and
    produces a faded, desaturated copy to visually convey "not included".

    Steps:
      1. Fully desaturate (grayscale)
      2. Slightly reduce brightness (0.85)
      3. Blend 50/50 with a white background for the faded look
      4. Save as JPEG (quality 90)
    """
    img = Image.open(src_path).convert("RGBA")

    # Desaturate: convert to grayscale and back
    gray = ImageEnhance.Color(img).enhance(0.0)

    # Reduce brightness slightly
    dimmed = ImageEnhance.Brightness(gray).enhance(0.85)

    # Blend with white at 50% to create the "faded" look
    white = Image.new("RGBA", dimmed.size, (255, 255, 255, 255))
    faded = Image.blend(white, dimmed, alpha=0.5)

    # Save as JPEG (no alpha)
    faded_rgb = faded.convert("RGB")
    faded_rgb.save(dst_path, "JPEG", quality=90)
    print(f"  Created shadowed: {os.path.basename(dst_path)}")


def upload_option_images(client, img_dir, option_groups):
    """Upload option images for all groups, auto-generating shadows for 'ohne'.

    Args:
        client: RattleClient instance
        img_dir: base directory containing the product's extracted images
        option_groups: list of group dicts, each with:
            {
                "name": "Group display name",
                "options": [
                    {
                        "id": <option_id>,
                        "label": "option label",
                        "image": "filename.jpg",       # source image
                        "ohne": True/False,             # optional, default False
                    },
                    ...
                ]
            }

    For any option with "ohne": True, the function will:
      - Look for the first non-ohne option in the same group that has an image
      - Generate a shadowed version of that image
      - Upload the shadow as the ohne option's image

    If an ohne option also specifies "image", that image is used as the
    shadow source instead of auto-detecting from the group.
    """
    shadow_dir = os.path.join(img_dir, "shadowed")
    os.makedirs(shadow_dir, exist_ok=True)

    total_uploaded = 0
    total_shadows = 0

    for group in option_groups:
        group_name = group["name"]
        options = group["options"]
        print(f"\n  --- {group_name} ---")

        # Collect the "mit" / specific options to know which image to shadow
        mit_image = None
        for opt in options:
            if not opt.get("ohne", False) and opt.get("image"):
                mit_image = opt["image"]
                break  # use the first one found as shadow source

        for opt in options:
            opt_id = opt["id"]
            label = opt.get("label", "")
            is_ohne = opt.get("ohne", False)

            if is_ohne:
                # Determine shadow source: explicit image on the ohne entry,
                # or fall back to the first mit image in the group.
                shadow_src_name = opt.get("image") or mit_image
                if not shadow_src_name:
                    print(
                        f"  SKIP option {opt_id} ({label}): "
                        f"no source image for shadow in group '{group_name}'"
                    )
                    continue

                src_path = os.path.join(img_dir, shadow_src_name)
                if not os.path.exists(src_path):
                    print(
                        f"  SKIP option {opt_id} ({label}): "
                        f"source image not found: {shadow_src_name}"
                    )
                    continue

                shadow_name = f"shadow_{shadow_src_name}"
                shadow_path = os.path.join(shadow_dir, shadow_name)

                # Only regenerate if missing or source is newer
                if not os.path.exists(shadow_path) or os.path.getmtime(src_path) > os.path.getmtime(
                    shadow_path
                ):
                    create_shadowed_image(src_path, shadow_path)
                    total_shadows += 1
                else:
                    print(f"  Reusing shadowed: {shadow_name}")

                _upload_one(client, opt_id, shadow_path, label)
                total_uploaded += 1

            else:
                image_name = opt.get("image")
                if not image_name:
                    print(f"  SKIP option {opt_id} ({label}): no image specified")
                    continue

                filepath = os.path.join(img_dir, image_name)
                if not os.path.exists(filepath):
                    print(f"  SKIP option {opt_id} ({label}): image not found: {image_name}")
                    continue

                _upload_one(client, opt_id, filepath, label)
                total_uploaded += 1

    print(f"\n  Shadows generated: {total_shadows}")
    print(f"  Total options uploaded: {total_uploaded}")


def _upload_one(client, option_id, filepath, label=""):
    """Upload a single option image."""
    try:
        result = client.upload_image(f"options/{option_id}/image", filepath)
        print(f"  OK option {option_id} ({label}): {os.path.basename(filepath)}")
        return result
    except Exception as e:
        print(f"  FAIL option {option_id} ({label}): {e}")
        return None
