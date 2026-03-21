"""Tests for source_reader.py — file listing and Excel parsing."""

import os
import pytest
from unittest.mock import patch, MagicMock


class TestListSources:
    """list_sources() — directory walking with dotfile filtering."""

    def test_returns_files_for_tenant(self, tmp_path):
        tenant_dir = tmp_path / "acme"
        tenant_dir.mkdir()
        (tenant_dir / "data.xlsx").write_text("x")
        (tenant_dir / "prices.json").write_text("x")

        with patch("source_reader.SOURCE_DIR", str(tmp_path)):
            from source_reader import list_sources
            files = list_sources("acme")

        assert sorted(files) == ["data.xlsx", "prices.json"]

    def test_ignores_dotfiles(self, tmp_path):
        tenant_dir = tmp_path / "acme"
        tenant_dir.mkdir()
        (tenant_dir / ".hidden").write_text("x")
        (tenant_dir / "visible.txt").write_text("x")

        with patch("source_reader.SOURCE_DIR", str(tmp_path)):
            from source_reader import list_sources
            files = list_sources("acme")

        assert files == ["visible.txt"]

    def test_includes_subdirectories(self, tmp_path):
        sub = tmp_path / "acme" / "pricelists"
        sub.mkdir(parents=True)
        (sub / "mecal.pdf").write_text("x")

        with patch("source_reader.SOURCE_DIR", str(tmp_path)):
            from source_reader import list_sources
            files = list_sources("acme")

        assert files == [os.path.join("pricelists", "mecal.pdf")]

    def test_nonexistent_tenant_returns_empty(self, tmp_path):
        with patch("source_reader.SOURCE_DIR", str(tmp_path)):
            from source_reader import list_sources
            assert list_sources("nonexistent") == []

    def test_empty_directory_returns_empty(self, tmp_path):
        (tmp_path / "empty").mkdir()
        with patch("source_reader.SOURCE_DIR", str(tmp_path)):
            from source_reader import list_sources
            assert list_sources("empty") == []

    def test_case_insensitive_tenant(self, tmp_path):
        (tmp_path / "acme").mkdir()
        (tmp_path / "acme" / "file.txt").write_text("x")

        with patch("source_reader.SOURCE_DIR", str(tmp_path)):
            from source_reader import list_sources
            # Tenant is lowercased in list_sources
            files = list_sources("ACME")

        assert files == ["file.txt"]

    def test_results_are_sorted(self, tmp_path):
        tenant_dir = tmp_path / "acme"
        tenant_dir.mkdir()
        for name in ["c.txt", "a.txt", "b.txt"]:
            (tenant_dir / name).write_text("x")

        with patch("source_reader.SOURCE_DIR", str(tmp_path)):
            from source_reader import list_sources
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

        with patch("source_reader.load_workbook", return_value=mock_wb):
            from source_reader import read_excel
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

        with patch("source_reader.load_workbook", return_value=mock_wb):
            from source_reader import read_excel
            result = read_excel("test.xlsx")

        assert result == [{"Name": "Drill", "col_1": "extra", "Price": 100}]

    def test_empty_file_returns_empty(self):
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = []
        mock_wb = MagicMock()
        mock_wb.active = mock_ws

        with patch("source_reader.load_workbook", return_value=mock_wb):
            from source_reader import read_excel
            assert read_excel("empty.xlsx") == []

    def test_header_only_returns_empty(self):
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = [("Name", "Price")]
        mock_wb = MagicMock()
        mock_wb.active = mock_ws

        with patch("source_reader.load_workbook", return_value=mock_wb):
            from source_reader import read_excel
            assert read_excel("headers-only.xlsx") == []

    def test_opens_read_only_and_data_only(self):
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = [("A",), (1,)]
        mock_wb = MagicMock()
        mock_wb.active = mock_ws

        with patch("source_reader.load_workbook", return_value=mock_wb) as mock_load:
            from source_reader import read_excel
            read_excel("test.xlsx")

        mock_load.assert_called_once_with("test.xlsx", read_only=True, data_only=True)

    def test_closes_workbook(self):
        mock_ws = MagicMock()
        mock_ws.iter_rows.return_value = [("A",), (1,)]
        mock_wb = MagicMock()
        mock_wb.active = mock_ws

        with patch("source_reader.load_workbook", return_value=mock_wb):
            from source_reader import read_excel
            read_excel("test.xlsx")

        mock_wb.close.assert_called_once()
