"""Tests for client.py — RattleClient HTTP wrapper, error handling, pagination."""

import json
import importlib
import pytest
from unittest.mock import MagicMock, patch, mock_open

from tests.conftest import make_response


@pytest.fixture
def client(monkeypatch):
    """Create a RattleClient with a mocked session."""
    monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key-123")
    import config
    importlib.reload(config)

    with patch("client.requests.Session") as mock_cls:
        session = MagicMock()
        mock_cls.return_value = session

        from client import RattleClient
        c = RattleClient("testco")
        c._session = session
        yield c, session


class TestClientInit:
    """RattleClient initialization."""

    def test_sets_auth_header(self, client):
        c, session = client
        session.headers.update.assert_called_once()
        call_args = session.headers.update.call_args[0][0]
        assert call_args["Authorization"] == "Bearer test-key-123"
        assert call_args["Accept"] == "application/json"

    def test_unknown_tenant_raises(self, monkeypatch):
        import config
        importlib.reload(config)
        with patch("client.requests.Session"):
            from client import RattleClient
            with pytest.raises(ValueError, match="Unknown tenant"):
                RattleClient("nonexistent")

    def test_base_url_stripped(self, client):
        c, _ = client
        assert not c.base_url.endswith("/")


class TestURLConstruction:
    """_url() path construction."""

    def test_simple_path(self, client):
        c, _ = client
        url = c._url("products")
        assert url.endswith("/products")

    def test_leading_slash_stripped(self, client):
        c, _ = client
        assert c._url("/products") == c._url("products")

    def test_nested_path(self, client):
        c, _ = client
        url = c._url("products/123/images")
        assert url.endswith("/products/123/images")


class TestHandleResponse:
    """_handle() response processing."""

    def test_success_returns_json(self, client):
        c, _ = client
        resp = make_response(200, json_data={"id": 1})
        assert c._handle(resp) == {"id": 1}

    def test_204_returns_none(self, client):
        c, _ = client
        resp = make_response(204, text="")
        resp.content = b""
        assert c._handle(resp) is None

    def test_empty_content_returns_none(self, client):
        c, _ = client
        resp = make_response(200)
        resp.content = b""
        assert c._handle(resp) is None

    def test_error_raises_runtime_error(self, client):
        c, _ = client
        resp = make_response(404, text="Not found", method="GET", url="http://test/products")
        with pytest.raises(RuntimeError, match="API error 404"):
            c._handle(resp)

    def test_error_includes_method_and_url(self, client):
        c, _ = client
        resp = make_response(500, text="Internal", method="POST", url="http://test/create")
        with pytest.raises(RuntimeError, match="POST"):
            c._handle(resp)

    def test_error_includes_response_text(self, client):
        c, _ = client
        resp = make_response(422, text="Validation failed")
        with pytest.raises(RuntimeError, match="Validation failed"):
            c._handle(resp)


class TestHTTPMethods:
    """GET, POST, PATCH, PUT, DELETE dispatch."""

    def test_get(self, client):
        c, session = client
        session.get.return_value = make_response(200, json_data={"ok": True})
        result = c.get("products", per_page=5)
        assert result == {"ok": True}
        session.get.assert_called_once()

    def test_get_passes_params(self, client):
        c, session = client
        session.get.return_value = make_response(200, json_data=[])
        c.get("products", per_page=10, status="active")
        _, kwargs = session.get.call_args
        assert kwargs["params"]["per_page"] == 10
        assert kwargs["params"]["status"] == "active"

    def test_post(self, client):
        c, session = client
        session.post.return_value = make_response(201, json_data={"id": "new"})
        result = c.post("products", json={"name": "Test"})
        assert result == {"id": "new"}

    def test_patch(self, client):
        c, session = client
        session.patch.return_value = make_response(200, json_data={"updated": True})
        result = c.patch("products/1", json={"name": "Updated"})
        assert result == {"updated": True}

    def test_put(self, client):
        c, session = client
        session.put.return_value = make_response(200, json_data={"replaced": True})
        result = c.put("products/1", json={"name": "Replaced"})
        assert result == {"replaced": True}

    def test_delete(self, client):
        c, session = client
        session.delete.return_value = make_response(204, text="")
        session.delete.return_value.content = b""
        result = c.delete("products/1")
        assert result is None


class TestListAll:
    """Cursor-based pagination via list_all()."""

    def test_returns_list_directly(self, client):
        """When API returns a plain list (no pagination)."""
        c, session = client
        session.get.return_value = make_response(200, json_data=[{"id": 1}, {"id": 2}])
        result = c.list_all("products")
        assert result == [{"id": 1}, {"id": 2}]

    def test_paginated_single_page(self, client):
        c, session = client
        session.get.return_value = make_response(200, json_data={
            "data": [{"id": 1}],
            "meta": {"next_cursor": None},
        })
        result = c.list_all("products")
        assert result == [{"id": 1}]

    def test_paginated_multiple_pages(self, client):
        c, session = client
        page1 = make_response(200, json_data={
            "data": [{"id": 1}],
            "meta": {"next_cursor": "cursor-2"},
        })
        page2 = make_response(200, json_data={
            "data": [{"id": 2}],
            "meta": {"next_cursor": None},
        })
        session.get.side_effect = [page1, page2]
        result = c.list_all("products")
        assert result == [{"id": 1}, {"id": 2}]
        assert session.get.call_count == 2

    def test_paginated_preserves_params(self, client):
        c, session = client
        page1 = make_response(200, json_data={
            "data": [{"id": 1}],
            "meta": {"next_cursor": "c2"},
        })
        page2 = make_response(200, json_data={
            "data": [{"id": 2}],
            "meta": {},
        })
        session.get.side_effect = [page1, page2]
        c.list_all("products", per_page=50)
        # Second call should include cursor
        _, kwargs = session.get.call_args
        assert kwargs["params"]["cursor"] == "c2"

    def test_empty_data(self, client):
        c, session = client
        session.get.return_value = make_response(200, json_data={
            "data": [],
            "meta": {},
        })
        result = c.list_all("products")
        assert result == []


class TestUploadImage:
    """Image upload via multipart form."""

    def test_upload_sends_file(self, client, tmp_path):
        c, session = client
        img_file = tmp_path / "test.jpg"
        img_file.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg")
        session.post.return_value = make_response(200, json_data={"url": "http://cdn/img.jpg"})
        result = c.upload_image("options/1/image", str(img_file))
        assert result == {"url": "http://cdn/img.jpg"}
        session.post.assert_called_once()

    def test_upload_custom_field_name(self, client, tmp_path):
        c, session = client
        img_file = tmp_path / "photo.jpg"
        img_file.write_bytes(b"\xff\xd8\xff\xe0fake")
        session.post.return_value = make_response(200, json_data={})
        c.upload_image("upload", str(img_file), field_name="photo")
        _, kwargs = session.post.call_args
        assert "photo" in kwargs["files"]


class TestIdempotency:
    """Verify operations are safe to retry."""

    def test_get_is_idempotent(self, client):
        c, session = client
        resp = make_response(200, json_data={"id": 1})
        session.get.return_value = resp
        r1 = c.get("products/1")
        r2 = c.get("products/1")
        assert r1 == r2

    def test_put_is_idempotent(self, client):
        c, session = client
        resp = make_response(200, json_data={"id": 1, "name": "A"})
        session.put.return_value = resp
        r1 = c.put("products/1", json={"name": "A"})
        r2 = c.put("products/1", json={"name": "A"})
        assert r1 == r2

    def test_patch_with_same_data(self, client):
        c, session = client
        resp = make_response(200, json_data={"updated": True})
        session.patch.return_value = resp
        r1 = c.patch("products/1", json={"description": "X"})
        r2 = c.patch("products/1", json={"description": "X"})
        assert r1 == r2
