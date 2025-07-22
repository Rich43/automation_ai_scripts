# ruff: noqa: E402
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "AutomationToolkit"
import sys

sys.path.insert(0, str(MODULE_PATH))

from logger_config import setup_logger, get_log_files, read_log_file


def test_setup_logger_creates_files(tmp_path, monkeypatch):
    logs_dir = tmp_path / "logs"
    monkeypatch.chdir(tmp_path)

    logger = setup_logger("test_logger")
    logger.info("hello")

    files = list(logs_dir.glob("*.log"))
    assert files
    assert any("automation" in f.name for f in files)


def test_get_log_files_and_read(tmp_path, monkeypatch):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    log_file = logs_dir / "test.log"
    log_file.write_text("line1\nline2\n")

    monkeypatch.chdir(tmp_path)

    files = get_log_files()
    assert len(files) == 1
    assert files[0]["name"] == "test.log"

    lines = read_log_file("test.log")
    assert lines == ["line1\n", "line2\n"]
