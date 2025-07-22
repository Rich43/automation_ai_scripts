# ruff: noqa: E402
import sys
from pathlib import Path
from types import SimpleNamespace

MODULE_PATH = Path(__file__).resolve().parents[1] / "AutomationToolkit"
sys.path.insert(0, str(MODULE_PATH))

from challenge_manager import ChallengeManager


def test_log_challenge_event_and_overall_progress(monkeypatch):
    def noop_load(self):
        self.challenges = {}

    monkeypatch.setattr(ChallengeManager, "_load_challenges", noop_load)
    cm = ChallengeManager()

    dummy = SimpleNamespace(status="completed")
    cm.challenges = {1: dummy}

    cm._log_challenge_event(1, "test", "msg")
    assert cm.challenge_logs[0]["event_type"] == "test"

    progress = cm.get_overall_progress()
    assert progress["total_challenges"] == 1
    assert progress["completed_challenges"] == 1
