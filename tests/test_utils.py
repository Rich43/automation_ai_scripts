# ruff: noqa: E402
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "AutomationToolkit"
sys.path.insert(0, str(MODULE_PATH))

from utils import (
    safe_filename,
    format_bytes,
    format_duration,
    validate_coordinates,
    clamp_coordinates,
    sanitize_log_message,
    PerformanceMonitor,
    hash_string,
    get_relative_time,
)

import time


def test_safe_filename():
    assert safe_filename('foo<>:"/\\|?*bar.txt') == "foo_________bar.txt"


def test_format_bytes():
    assert format_bytes(500) == "500.0 B"
    assert format_bytes(2048) == "2.0 KB"


def test_format_duration():
    assert format_duration(30) == "30.0s"
    assert format_duration(90) == "1.5m"
    assert format_duration(7200) == "2.0h"


def test_validate_and_clamp_coordinates():
    assert validate_coordinates(10, 10, 100, 100)
    assert not validate_coordinates(-1, 50, 100, 100)
    assert clamp_coordinates(-5, 105, 100, 100) == (0, 100)


def test_sanitize_log_message():
    assert sanitize_log_message("hello\x00world") == "helloworld"
    assert len(sanitize_log_message("a" * 2000)) == 1000


def test_performance_monitor():
    pm = PerformanceMonitor()
    pm.start()
    time.sleep(0.01)
    pm.checkpoint("step")
    result = pm.finish()
    assert result["checkpoint_count"] == 1
    assert result["total_time"] >= 0


def test_hash_and_relative_time():
    h = hash_string("test")
    assert h == hash_string("test")
    assert len(h) == 64
    now = time.time()
    assert get_relative_time(now) == "0 seconds ago"
