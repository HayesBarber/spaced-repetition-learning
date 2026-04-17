from datetime import timedelta
from types import SimpleNamespace

from srl.commands import add, list_, nextup, pause
from srl.commands import resume
from srl.utils import today


def test_pause_sets_paused_state(console, load_json, mock_data):
    pause.handle(SimpleNamespace(), console)

    pause_data = load_json(mock_data.PAUSE_FILE)
    assert pause_data["paused_on"] == today().isoformat()

    output = console.export_text()
    assert "Paused" in output
    assert "srl resume" in output


def test_pause_twice_reports_existing_state(console):
    pause.handle(SimpleNamespace(), console)
    pause.handle(SimpleNamespace(), console)

    output = console.export_text()
    assert "already paused" in output


def test_list_uses_frozen_schedule_while_paused(
    console, load_json, dump_json, mock_data, monkeypatch
):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    add.handle(SimpleNamespace(name="Soon Due", rating=3), console)
    add.handle(SimpleNamespace(name="Later Problem", rating=5), console)
    console.clear()

    data = load_json(mock_data.PROGRESS_FILE)
    data["Soon Due"]["history"][-1]["date"] = (today() - timedelta(days=5)).isoformat()
    data["Later Problem"]["history"][-1]["date"] = (
        today() - timedelta(days=2)
    ).isoformat()
    dump_json(mock_data.PROGRESS_FILE, data)

    dump_json(mock_data.PAUSE_FILE, {"paused_on": (today() - timedelta(days=2)).isoformat()})

    list_.handle(SimpleNamespace(n=None, url=False), console)

    output = console.export_text()
    assert "Schedule paused since" in output
    assert "Soon Due" in output
    assert "Later Problem" not in output


def test_resume_shifts_schedule_by_elapsed_days(
    console, load_json, dump_json, mock_data, monkeypatch
):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    add.handle(SimpleNamespace(name="Soon Due", rating=3), console)
    add.handle(SimpleNamespace(name="Later Problem", rating=5), console)
    console.clear()

    data = load_json(mock_data.PROGRESS_FILE)
    data["Soon Due"]["history"][-1]["date"] = (today() - timedelta(days=4)).isoformat()
    data["Later Problem"]["history"][-1]["date"] = (
        today() - timedelta(days=2)
    ).isoformat()
    dump_json(mock_data.PROGRESS_FILE, data)
    dump_json(mock_data.PAUSE_FILE, {"paused_on": (today() - timedelta(days=2)).isoformat()})

    resume.handle(SimpleNamespace(), console)

    updated = load_json(mock_data.PROGRESS_FILE)
    assert updated["Soon Due"]["history"][-1]["date"] == (
        today() - timedelta(days=2)
    ).isoformat()
    assert updated["Later Problem"]["history"][-1]["date"] == today().isoformat()
    assert load_json(mock_data.PAUSE_FILE) == {}

    output = console.export_text()
    assert "Resumed" in output
    assert "2 paused days" in output

    console.clear()
    list_.handle(SimpleNamespace(n=None, url=False), console)

    output = console.export_text()
    assert "No problems due today or in Next Up" in output


def test_pause_defaults_to_one_day(console, load_json, dump_json, mock_data):
    pause.handle(SimpleNamespace(), console)
    assert load_json(mock_data.PAUSE_FILE)["paused_on"] == today().isoformat()


def test_pause_skips_nextup_and_mastered(console, load_json, mock_data):
    add.handle(SimpleNamespace(name="Mastered Problem", rating=5), console)
    add.handle(SimpleNamespace(name="Mastered Problem", rating=5), console)
    nextup.handle(SimpleNamespace(action="add", name="Queued Problem"), console)
    console.clear()

    pause.handle(SimpleNamespace(), console)

    mastered = load_json(mock_data.MASTERED_FILE)
    next_up = load_json(mock_data.NEXT_UP_FILE)

    assert "Mastered Problem" in mastered
    assert next_up["Queued Problem"]["added"] == today().isoformat()


def test_resume_without_pause(console):
    resume.handle(SimpleNamespace(), console)

    output = console.export_text()
    assert "Schedule is not paused" in output


def test_add_auto_resumes_schedule(console, load_json, dump_json, mock_data):
    add.handle(SimpleNamespace(name="Problem A", rating=3), console)
    console.clear()

    data = load_json(mock_data.PROGRESS_FILE)
    data["Problem A"]["history"][-1]["date"] = (today() - timedelta(days=4)).isoformat()
    dump_json(mock_data.PROGRESS_FILE, data)
    dump_json(mock_data.PAUSE_FILE, {"paused_on": (today() - timedelta(days=2)).isoformat()})

    add.handle(SimpleNamespace(name="Problem A", rating=4), console)

    progress = load_json(mock_data.PROGRESS_FILE)
    history = progress["Problem A"]["history"]

    assert history[0]["date"] == (today() - timedelta(days=2)).isoformat()
    assert history[1]["date"] == today().isoformat()
    assert history[1]["rating"] == 4
    assert load_json(mock_data.PAUSE_FILE) == {}

    output = console.export_text()
    assert "Automatically resumed" in output


def test_audit_pass_auto_resumes_schedule(console, load_json, dump_json, mock_data):
    from srl.commands import audit

    dump_json(mock_data.AUDIT_FILE, {"current_audit": "Audit Problem"})
    dump_json(mock_data.PAUSE_FILE, {"paused_on": (today() - timedelta(days=3)).isoformat()})

    audit.handle_pass(SimpleNamespace(), console)

    assert load_json(mock_data.PAUSE_FILE) == {}
    output = console.export_text()
    assert "Automatically resumed" in output
    assert "Audit passed!" in output
