# ruff: noqa: E402
from pathlib import Path
import sys

MODULE_PATH = Path(__file__).resolve().parents[1] / "AutomationToolkit"
sys.path.insert(0, str(MODULE_PATH))

from system_detector import SystemDetector


def test_get_system_paths_has_home_and_temp():
    detector = SystemDetector()
    paths = detector.get_system_paths()
    assert "home" in paths
    assert Path(paths["home"]).exists()
    assert "temp" in paths


def test_is_process_running_self():
    detector = SystemDetector()
    assert detector.is_process_running("python") is True
