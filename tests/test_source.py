"""Tests for rattle_api.source — file listing, Excel/PDF/DOCX parsing."""

import os
from unittest.mock import MagicMock, patch

import pytest


class TestListSources:
    """list_sources() — directory walking with dotfile filtering."""

    def test_returns_files_for_tenant(self, tmp_path):
        tenant_dir = tmp_path / "acme"
        tenant_dir.mkdir()
        (tenant_dir / "data.xlsx").write_text("x")
        (tenant_dir / "prices.json").write_text("x")

        with patch("rattle_api.source.SOURCE_DIR", str(tmp_path)):
            from rattle_api.source import list_sources

            files = list_sources("acme")

        assert sorted(files) == ["data.xlsx", "prices.json"]

    def test_ignores_dotfiles(self, tmp_path):
        tenant_dir = tmp_path / "acme"
        tenant_dir.mkdir()
        (tenant_dir / ".hidden").write_text("x")
        (tenant_dir / "visible.txt").write_text("x")

        with patch("rattle_api.source.SOURCE_DIR", str(tmp_path)):
            from rattle_api.source import list_sources

            files = list_sources("acme")

        assert files == ["visible.txt"]

    def test_includes_subdirectories(self, tmp_path):
        sub = tmp_path / "acme" / "pricelists"
        sub.mkdir(parents=True)
        (sub / "mecal.pdf").write_text("x")

        with patch("rattle_api.source.SOURCE_DIR", str(tmp_path)):
            from rattle_api.source import list_sources

            files = list_sources("acme")

        assert files == [os.path.join("pricelists", "mecal.pdf")]

    def test_nonexistent_tenant_returns_empty(self, tmp_path):
        with patch("rattle_api.source.SOURCE_DIR", str(tmp_path)):
            from rattle_api.source import list_sources

            assert list_sources("nonexistent") == []

    def test_empty_directory_returns_empty(self, tmp_path):
        (tmp_path / "empty").mkdir()
        with patch("rattle_api.source.SOURCE_DIR", str(tmp_path)):
            from rattle_api.source import list_sources

            assert list_sources("empty") == []

    def test_case_insensitive_tenant(self, tmp_path):
        (tmp_path / "acme").mkdir()
        (tmp_path / "acme" / "file.txt").write_text("x")

        with patch("rattle_api.source.SOURCE_DIR", str(tmp_path)):
            from rattle_api.source import list_sources

            # Tenant is lowercased in list_sources
            files = list_sources("ACME")

        assert files == ["file.txt"]

    def test_results_are_sorted(self, tmp_path):
        tenant_dir = tmp_path / "acme"
        tenant_dir.mkdir()
        for name in ["c.txt", "a.txt", "b.txt"]:
            (tenant_dir / name).write_text("x")

        with patch("rattle_api.source.SOURCE_DIR", str(tmp_path)):
            from rattle_api.source import list_sources

            files = list_sources("acme")

        assert files == ["a.txt", "b.txt", "c.txt"]


class TestReadExcel:
    """read_excel() — openpyxl worksheet parsing."""

    def test_reads_headers_and_rows(self):
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = [
            ("Name", "Price"),
            ("Drill", 100),
            ("Saw", 200),
        ]
        mock_wb = MagicMock()
        mock_wb.active = mock_ws

        with patch("rattle_api.source.load_workbook", return_value=mock_wb):
            from rattle_api.source import read_excel

            result = read_excel("test.xlsx")

        assert result == [
            {"Name": "Drill", "Price": 100},
            {"Name": "Saw", "Price": 200},
        ]

    def test_none_header_gets_col_index(self):
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = [
            ("Name", None, "Price"),
            ("Drill", "extra", 100),
        ]
        mock_wb = MagicMock()
        mock_wb.active = mock_ws

        with patch("rattle_api.source.load_workbook", return_value=mock_wb):
            from rattle_api.source import read_excel

            result = read_excel("test.xlsx")

        assert result == [{"Name": "Drill", "col_1": "extra", "Price": 100}]

    def test_empty_file_returns_empty(self):
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = []
        mock_wb = MagicMock()
        mock_wb.active = mock_ws

        with patch("rattle_api.source.load_workbook", return_value=mock_wb):
            from rattle_api.source import read_excel

            assert read_excel("empty.xlsx") == []

    def test_header_only_returns_empty(self):
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = [("Name", "Price")]
        mock_wb = MagicMock()
        mock_wb.active = mock_ws

        with patch("rattle_api.source.load_workbook", return_value=mock_wb):
            from rattle_api.source import read_excel

            assert read_excel("headers-only.xlsx") == []

    def test_opens_read_only_and_data_only(self):
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = [("A",), (1,)]
        mock_wb = MagicMock()
        mock_wb.active = mock_ws

        with patch("rattle_api.source.load_workbook", return_value=mock_wb) as mock_load:
            from rattle_api.source import read_excel

            read_excel("test.xlsx")

        mock_load.assert_called_once_with("test.xlsx", read_only=True, data_only=True)

    def test_closes_workbook(self):
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = [("A",), (1,)]
        mock_wb = MagicMock()
        mock_wb.active = mock_ws

        with patch("rattle_api.source.load_workbook", return_value=mock_wb):
            from rattle_api.source import read_excel

            read_excel("test.xlsx")

        mock_wb.close.assert_called_once()


# ---------------------------------------------------------------------------
# read_pdf
# ---------------------------------------------------------------------------


class TestReadPdf:
    """read_pdf() — PDF text extraction via pymupdf."""

    def test_extracts_text(self):
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Page 1 content"
        mock_doc = MagicMock()
        mock_doc.__iter__ = lambda self: iter([mock_page])

        with patch.dict("sys.modules", {"fitz": MagicMock()}):
            import sys

            sys.modules["fitz"].open.return_value = mock_doc
            from rattle_api.source import read_pdf

            result = read_pdf("test.pdf")

        assert "Page 1 content" in result

    def test_joins_multiple_pages(self):
        pages = [MagicMock(), MagicMock()]
        pages[0].get_text.return_value = "Page 1"
        pages[1].get_text.return_value = "Page 2"
        mock_doc = MagicMock()
        mock_doc.__iter__ = lambda self: iter(pages)

        with patch.dict("sys.modules", {"fitz": MagicMock()}):
            import sys

            sys.modules["fitz"].open.return_value = mock_doc
            from rattle_api.source import read_pdf

            result = read_pdf("test.pdf")

        assert "Page 1" in result
        assert "Page 2" in result

    def test_closes_document(self):
        mock_doc = MagicMock()
        mock_doc.__iter__ = lambda self: iter([])

        with patch.dict("sys.modules", {"fitz": MagicMock()}):
            import sys

            sys.modules["fitz"].open.return_value = mock_doc
            from rattle_api.source import read_pdf

            read_pdf("test.pdf")

        mock_doc.close.assert_called_once()

    def test_import_error_message(self):
        with patch.dict("sys.modules", {"fitz": None}):
            with pytest.raises(ImportError, match="pymupdf"):
                from importlib import reload

                import rattle_api.source as src

                reload(src)
                src.read_pdf("test.pdf")


# ---------------------------------------------------------------------------
# read_docx
# ---------------------------------------------------------------------------


class TestReadDocx:
    """read_docx() — Word document text extraction via python-docx."""

    def test_extracts_paragraphs(self):
        mock_para1 = MagicMock()
        mock_para1.text = "First paragraph"
        mock_para2 = MagicMock()
        mock_para2.text = "Second paragraph"
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_para1, mock_para2]

        mock_docx = MagicMock()
        mock_docx.Document.return_value = mock_doc

        with patch.dict("sys.modules", {"docx": mock_docx}):
            from rattle_api.source import read_docx

            result = read_docx("test.docx")

        assert "First paragraph" in result
        assert "Second paragraph" in result

    def test_empty_doc_returns_empty_string(self):
        mock_doc = MagicMock()
        mock_doc.paragraphs = []
        mock_docx = MagicMock()
        mock_docx.Document.return_value = mock_doc

        with patch.dict("sys.modules", {"docx": mock_docx}):
            from rattle_api.source import read_docx

            result = read_docx("empty.docx")

        assert result == ""

    def test_import_error_message(self):
        with patch.dict("sys.modules", {"docx": None}):
            with pytest.raises(ImportError, match="python-docx"):
                from importlib import reload

                import rattle_api.source as src

                reload(src)
                src.read_docx("test.docx")


# ---------------------------------------------------------------------------
# read_source (dispatcher)
# ---------------------------------------------------------------------------


class TestReadSource:
    """read_source() — dispatch by file extension."""

    def test_xlsx_dispatches_to_read_excel(self):
        with patch("rattle_api.source.read_excel", return_value=[{"A": 1}]) as mock:
            from rattle_api.source import read_source

            result = read_source("data.xlsx")

        mock.assert_called_once_with("data.xlsx")
        assert result["type"] == "excel"
        assert result["data"] == [{"A": 1}]
        assert result["filename"] == "data.xlsx"

    def test_xlsm_dispatches_to_read_excel(self):
        with patch("rattle_api.source.read_excel", return_value=[]) as mock:
            from rattle_api.source import read_source

            result = read_source("macro.xlsm")

        mock.assert_called_once_with("macro.xlsm")
        assert result["type"] == "excel"

    def test_pdf_dispatches_to_read_pdf(self):
        with patch("rattle_api.source.read_pdf", return_value="PDF text") as mock:
            from rattle_api.source import read_source

            result = read_source("doc.pdf")

        mock.assert_called_once_with("doc.pdf")
        assert result["type"] == "pdf"
        assert result["data"] == "PDF text"

    def test_docx_dispatches_to_read_docx(self):
        with patch("rattle_api.source.read_docx", return_value="Word text") as mock:
            from rattle_api.source import read_source

            result = read_source("doc.docx")

        mock.assert_called_once_with("doc.docx")
        assert result["type"] == "docx"
        assert result["data"] == "Word text"

    def test_unsupported_extension_raises(self):
        from rattle_api.source import read_source

        with pytest.raises(ValueError, match="Unsupported"):
            read_source("data.csv")

    def test_case_insensitive_extension(self):
        with patch("rattle_api.source.read_pdf", return_value="text"):
            from rattle_api.source import read_source

            result = read_source("DOC.PDF")

        assert result["type"] == "pdf"
