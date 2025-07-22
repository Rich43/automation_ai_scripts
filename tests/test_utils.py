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
    ensure_directory,
    generate_unique_id,
    run_command,
    create_backup_filename,
    load_json_file,
    save_json_file,
    get_timestamp,
    format_timestamp,
    retry_with_backoff,
    debounce,
    timeout_handler,
    find_available_port,
    get_process_by_name,
    kill_process_tree,
)

import time
import subprocess
import socket
import psutil
import pytest


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


def test_ensure_directory(tmp_path):
    path = tmp_path / "subdir"
    result = ensure_directory(path)
    assert result.exists()
    assert result.is_dir()


def test_generate_unique_id_unique():
    first = generate_unique_id()
    second = generate_unique_id()
    assert first != second


def test_run_command_success():
    result = run_command(["echo", "hello"])
    assert result["success"] is True
    assert "hello" in result["stdout"]


def test_create_backup_filename(tmp_path):
    original = tmp_path / "file.txt"
    original.write_text("x")
    backup = create_backup_filename(original)
    assert backup.parent == tmp_path
    assert backup.name.startswith("file_backup_")
    assert backup.suffix == ".txt"


def test_load_and_save_json_file(tmp_path):
    data = {"x": 1}
    file_path = tmp_path / "data.json"
    assert save_json_file(data, file_path) is True
    loaded = load_json_file(file_path)
    assert loaded == data


def test_load_json_file_invalid(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{")
    assert load_json_file(bad_file) is None


def test_format_and_get_timestamp():
    ts = get_timestamp()
    assert abs(time.time() - ts) < 1
    assert format_timestamp(0) == "1970-01-01 00:00:00"


def test_retry_with_backoff(monkeypatch):
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("fail")
        return "ok"

    wrapped = retry_with_backoff(flaky, max_attempts=3, base_delay=0.01)
    assert wrapped() == "ok"
    assert calls["n"] == 3


def test_debounce():
    results = []

    @debounce(0.1)
    def func(x):
        results.append(x)
        return x

    first = func(1)
    second = func(2)
    time.sleep(0.11)
    third = func(3)

    assert first == 1
    assert second is None
    assert third == 3
    assert results == [1, 3]


def test_timeout_handler():
    @timeout_handler(1)
    def slow():
        time.sleep(2)

    with pytest.raises(TimeoutError):
        slow()


def test_find_available_port():
    port = find_available_port(start_port=5000, max_attempts=10)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", port))
    s.close()


def test_run_command_failure():
    result = run_command(["false"])
    assert result["success"] is False


def test_get_process_by_name():
    procs = get_process_by_name("python")
    assert any("python" in p["name"].lower() for p in procs)


def test_kill_process_tree():
    proc = subprocess.Popen(["sleep", "1"])
    assert kill_process_tree(proc.pid)
    assert not psutil.pid_exists(proc.pid)
