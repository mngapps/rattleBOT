"""Tests for image_utils.py — shadow generation and option image upload."""

import os
from unittest.mock import MagicMock

import pytest


class TestCreateShadowedImage:
    """create_shadowed_image() — greyed-out 'ohne' variant generation."""

    def test_creates_output_file(self, tmp_path):
        """Shadow image is created at the destination path."""
        from PIL import Image
        # Create a simple test image
        src = tmp_path / "source.png"
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img.save(str(src))

        dst = tmp_path / "shadow.jpg"
        from image_utils import create_shadowed_image
        create_shadowed_image(str(src), str(dst))

        assert dst.exists()
        assert dst.stat().st_size > 0

    def test_output_is_jpeg(self, tmp_path):
        from PIL import Image
        src = tmp_path / "source.png"
        Image.new("RGB", (50, 50), color=(0, 128, 255)).save(str(src))

        dst = tmp_path / "shadow.jpg"
        from image_utils import create_shadowed_image
        create_shadowed_image(str(src), str(dst))

        result = Image.open(str(dst))
        assert result.format == "JPEG"

    def test_output_is_desaturated(self, tmp_path):
        """Shadow should be significantly less colorful than the original."""
        from PIL import Image
        src = tmp_path / "colorful.png"
        Image.new("RGB", (50, 50), color=(255, 0, 0)).save(str(src))

        dst = tmp_path / "shadow.jpg"
        from image_utils import create_shadowed_image
        create_shadowed_image(str(src), str(dst))

        result = Image.open(str(dst))
        r, g, b = result.getpixel((25, 25))
        # In a desaturated + faded red, all channels should be close
        assert abs(r - g) < 30
        assert abs(r - b) < 30

    def test_output_is_faded(self, tmp_path):
        """Shadow should be lighter (blended with white)."""
        from PIL import Image
        src = tmp_path / "dark.png"
        Image.new("RGB", (50, 50), color=(0, 0, 0)).save(str(src))

        dst = tmp_path / "shadow.jpg"
        from image_utils import create_shadowed_image
        create_shadowed_image(str(src), str(dst))

        result = Image.open(str(dst))
        r, g, b = result.getpixel((25, 25))
        # Black blended with white at 50% should be ~128
        assert r > 100  # significantly lighter than pure black

    def test_preserves_dimensions(self, tmp_path):
        from PIL import Image
        src = tmp_path / "sized.png"
        Image.new("RGB", (200, 300), color=(100, 100, 100)).save(str(src))

        dst = tmp_path / "shadow.jpg"
        from image_utils import create_shadowed_image
        create_shadowed_image(str(src), str(dst))

        result = Image.open(str(dst))
        assert result.size == (200, 300)

    def test_idempotent_result(self, tmp_path):
        """Running shadow generation twice on same source produces identical output."""
        from PIL import Image
        src = tmp_path / "source.png"
        Image.new("RGB", (50, 50), color=(100, 200, 50)).save(str(src))

        dst1 = tmp_path / "shadow1.jpg"
        dst2 = tmp_path / "shadow2.jpg"
        from image_utils import create_shadowed_image
        create_shadowed_image(str(src), str(dst1))
        create_shadowed_image(str(src), str(dst2))

        img1 = Image.open(str(dst1))
        img2 = Image.open(str(dst2))
        assert list(img1.tobytes()) == list(img2.tobytes())


class TestUploadOptionImages:
    """upload_option_images() — declarative upload with shadow auto-generation."""

    @pytest.fixture
    def img_dir(self, tmp_path):
        """Create a temp directory with test images."""
        from PIL import Image
        d = tmp_path / "images"
        d.mkdir()
        Image.new("RGB", (50, 50), color=(255, 0, 0)).save(str(d / "drill.jpg"))
        Image.new("RGB", (50, 50), color=(0, 255, 0)).save(str(d / "saw.jpg"))
        return d

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.upload_image.return_value = {"url": "http://cdn/img.jpg"}
        return client

    def test_uploads_regular_option(self, mock_client, img_dir):
        from image_utils import upload_option_images
        groups = [{
            "name": "Tools",
            "options": [
                {"id": "opt1", "label": "With drill", "image": "drill.jpg"},
            ],
        }]
        upload_option_images(mock_client, str(img_dir), groups)
        mock_client.upload_image.assert_called_once()

    def test_generates_shadow_for_ohne(self, mock_client, img_dir):
        from image_utils import upload_option_images
        groups = [{
            "name": "Tools",
            "options": [
                {"id": "opt1", "label": "With drill", "image": "drill.jpg"},
                {"id": "opt2", "label": "Without drill", "ohne": True},
            ],
        }]
        upload_option_images(mock_client, str(img_dir), groups)

        shadow_dir = img_dir / "shadowed"
        assert shadow_dir.exists()
        shadow_files = list(shadow_dir.iterdir())
        assert len(shadow_files) == 1
        assert "shadow_" in shadow_files[0].name

    def test_ohne_uses_explicit_image(self, mock_client, img_dir):
        from image_utils import upload_option_images
        groups = [{
            "name": "Tools",
            "options": [
                {"id": "opt1", "label": "With drill", "image": "drill.jpg"},
                {"id": "opt2", "label": "Without saw", "image": "saw.jpg", "ohne": True},
            ],
        }]
        upload_option_images(mock_client, str(img_dir), groups)

        shadow_dir = img_dir / "shadowed"
        shadow_files = list(shadow_dir.iterdir())
        assert any("saw" in f.name for f in shadow_files)

    def test_skips_ohne_without_source(self, mock_client, img_dir, capsys):
        from image_utils import upload_option_images
        groups = [{
            "name": "Empty",
            "options": [
                {"id": "opt1", "label": "Without", "ohne": True},
            ],
        }]
        upload_option_images(mock_client, str(img_dir), groups)
        captured = capsys.readouterr()
        assert "SKIP" in captured.out

    def test_skips_missing_image(self, mock_client, img_dir, capsys):
        from image_utils import upload_option_images
        groups = [{
            "name": "Tools",
            "options": [
                {"id": "opt1", "label": "Missing", "image": "nonexistent.jpg"},
            ],
        }]
        upload_option_images(mock_client, str(img_dir), groups)
        captured = capsys.readouterr()
        assert "SKIP" in captured.out
        mock_client.upload_image.assert_not_called()

    def test_skips_option_without_image(self, mock_client, img_dir, capsys):
        from image_utils import upload_option_images
        groups = [{
            "name": "Tools",
            "options": [
                {"id": "opt1", "label": "No image"},
            ],
        }]
        upload_option_images(mock_client, str(img_dir), groups)
        captured = capsys.readouterr()
        assert "SKIP" in captured.out

    def test_reuses_existing_shadow(self, mock_client, img_dir, capsys):
        """If shadow already exists and source hasn't changed, reuse it."""
        from PIL import Image

        from image_utils import upload_option_images

        # Pre-create shadow
        shadow_dir = img_dir / "shadowed"
        shadow_dir.mkdir()
        Image.new("RGB", (50, 50)).save(str(shadow_dir / "shadow_drill.jpg"))

        # Make shadow newer than source
        src_time = os.path.getmtime(str(img_dir / "drill.jpg"))
        os.utime(str(shadow_dir / "shadow_drill.jpg"), (src_time + 10, src_time + 10))

        groups = [{
            "name": "Tools",
            "options": [
                {"id": "opt1", "label": "With", "image": "drill.jpg"},
                {"id": "opt2", "label": "Without", "ohne": True},
            ],
        }]
        upload_option_images(mock_client, str(img_dir), groups)
        captured = capsys.readouterr()
        assert "Reusing" in captured.out

    def test_upload_failure_handled(self, mock_client, img_dir, capsys):
        mock_client.upload_image.side_effect = RuntimeError("Upload failed")
        from image_utils import upload_option_images
        groups = [{
            "name": "Tools",
            "options": [
                {"id": "opt1", "label": "Drill", "image": "drill.jpg"},
            ],
        }]
        # Should not raise
        upload_option_images(mock_client, str(img_dir), groups)
        captured = capsys.readouterr()
        assert "FAIL" in captured.out

    def test_multiple_groups(self, mock_client, img_dir):
        from image_utils import upload_option_images
        groups = [
            {
                "name": "Drills",
                "options": [{"id": "opt1", "label": "Drill", "image": "drill.jpg"}],
            },
            {
                "name": "Saws",
                "options": [{"id": "opt2", "label": "Saw", "image": "saw.jpg"}],
            },
        ]
        upload_option_images(mock_client, str(img_dir), groups)
        assert mock_client.upload_image.call_count == 2
