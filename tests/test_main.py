"""Tests for rattle_api.main — CLI argument parsing and command dispatch."""

import importlib
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def setup_tenant(monkeypatch):
    """Ensure a tenant is available for CLI tests."""
    monkeypatch.setenv("RATTLE_API_KEY_TESTCO", "test-key")
    import rattle_api.config as config

    importlib.reload(config)


class TestCLIParsing:
    """Argument parsing for all commands."""

    def test_test_connection(self):
        with patch("sys.argv", ["main.py", "testco", "test-connection"]):
            with patch("rattle_api.main.cmd_test_connection") as mock_cmd:
                from rattle_api.main import main

                main()
                mock_cmd.assert_called_once()
                args = mock_cmd.call_args[0]
                assert args[0] == "testco"

    def test_list_sources(self):
        with patch("sys.argv", ["main.py", "testco", "list-sources"]):
            with patch("rattle_api.main.cmd_list_sources") as mock_cmd:
                from rattle_api.main import main

                main()
                mock_cmd.assert_called_once()

    def test_ai_describe_defaults(self):
        with patch("sys.argv", ["main.py", "testco", "ai-describe"]):
            with patch("rattle_api.main.cmd_ai_describe") as mock_cmd:
                from rattle_api.main import main

                main()
                args_obj = mock_cmd.call_args[0][1]
                assert args_obj.limit == 5
                assert args_obj.language == "de"

    def test_ai_describe_custom(self):
        argv = ["main.py", "testco", "ai-describe", "--limit", "10", "--language", "en"]
        with patch("sys.argv", argv):
            with patch("rattle_api.main.cmd_ai_describe") as mock_cmd:
                from rattle_api.main import main

                main()
                args_obj = mock_cmd.call_args[0][1]
                assert args_obj.limit == 10
                assert args_obj.language == "en"

    def test_ai_classify_defaults(self):
        with patch("sys.argv", ["main.py", "testco", "ai-classify"]):
            with patch("rattle_api.main.cmd_ai_classify") as mock_cmd:
                from rattle_api.main import main

                main()
                args_obj = mock_cmd.call_args[0][1]
                assert args_obj.limit == 10

    def test_ai_transform_args(self):
        argv = ["main.py", "testco", "ai-transform", "datanorm", "rattle", "data.json", "--push"]
        with patch("sys.argv", argv):
            with patch("rattle_api.main.cmd_ai_transform") as mock_cmd:
                from rattle_api.main import main

                main()
                args_obj = mock_cmd.call_args[0][1]
                assert args_obj.source_format == "datanorm"
                assert args_obj.target_format == "rattle"
                assert args_obj.data_file == "data.json"
                assert args_obj.push is True

    def test_ai_transform_no_push(self):
        argv = ["main.py", "testco", "ai-transform", "eclass", "bmecat", "in.json"]
        with patch("sys.argv", argv):
            with patch("rattle_api.main.cmd_ai_transform") as mock_cmd:
                from rattle_api.main import main

                main()
                args_obj = mock_cmd.call_args[0][1]
                assert args_obj.push is False

    def test_ai_analyse_custom_question(self):
        with patch("sys.argv", ["main.py", "testco", "ai-analyse", "--question", "How many?"]):
            with patch("rattle_api.main.cmd_ai_analyse") as mock_cmd:
                from rattle_api.main import main

                main()
                args_obj = mock_cmd.call_args[0][1]
                assert args_obj.question == "How many?"

    def test_ai_analyse_default_question(self):
        with patch("sys.argv", ["main.py", "testco", "ai-analyse"]):
            with patch("rattle_api.main.cmd_ai_analyse") as mock_cmd:
                from rattle_api.main import main

                main()
                args_obj = mock_cmd.call_args[0][1]
                assert args_obj.question is None

    def test_ai_providers(self):
        with patch("sys.argv", ["main.py", "testco", "ai-providers"]):
            with patch("rattle_api.main.cmd_ai_providers") as mock_cmd:
                from rattle_api.main import main

                main()
                mock_cmd.assert_called_once()

    def test_missing_command_exits(self):
        with patch("sys.argv", ["main.py", "testco"]):
            with pytest.raises(SystemExit):
                from rattle_api.main import main

                main()

    def test_missing_tenant_exits(self):
        with patch("sys.argv", ["main.py"]):
            with pytest.raises(SystemExit):
                from rattle_api.main import main

                main()


class TestCommandDispatch:
    """Commands dispatch to the correct handler functions."""

    def test_all_commands_registered(self):
        # Verify command mapping covers all subparsers
        expected = {
            "test-connection",
            "list-sources",
            "ai-describe",
            "ai-classify",
            "ai-transform",
            "ai-analyse",
            "ai-providers",
        }
        # Read the commands dict from main module
        import rattle_api.main as main_mod

        # The commands dict is inside main() — test by calling each
        for cmd in expected:
            argv = ["main.py", "testco", cmd]
            if cmd == "ai-transform":
                argv += ["src", "dst", "file.json"]
            with patch("sys.argv", argv):
                handler = f"rattle_api.main.cmd_{cmd.replace('-', '_')}"
                with patch(handler) as mock_h:
                    main_mod.main()
                    mock_h.assert_called_once()


class TestCommandTestConnection:
    """cmd_test_connection — verify API connectivity."""

    def test_prints_ok_on_success(self, capsys):
        with patch("rattle_api.main.RattleClient") as mock_cls:
            mock_client = MagicMock()
            mock_client.get.return_value = {"data": []}
            mock_cls.return_value = mock_client

            from rattle_api.main import cmd_test_connection

            cmd_test_connection("testco", MagicMock())

        captured = capsys.readouterr()
        assert "OK" in captured.out

    def test_exits_on_failure(self):
        with patch("rattle_api.main.RattleClient") as mock_cls:
            mock_client = MagicMock()
            mock_client.get.side_effect = RuntimeError("Connection refused")
            mock_cls.return_value = mock_client

            from rattle_api.main import cmd_test_connection

            with pytest.raises(SystemExit):
                cmd_test_connection("testco", MagicMock())


class TestCommandListSources:
    """cmd_list_sources — list source files."""

    def test_prints_files(self, capsys):
        with patch("rattle_api.main.list_sources", return_value=["a.xlsx", "b.json"]):
            from rattle_api.main import cmd_list_sources

            cmd_list_sources("testco", MagicMock())

        captured = capsys.readouterr()
        assert "a.xlsx" in captured.out
        assert "b.json" in captured.out

    def test_no_files_message(self, capsys):
        with patch("rattle_api.main.list_sources", return_value=[]):
            from rattle_api.main import cmd_list_sources

            cmd_list_sources("testco", MagicMock())

        captured = capsys.readouterr()
        assert "No source files" in captured.out
