from srl.commands import list_, add, nextup
from types import SimpleNamespace
import json
from datetime import datetime, timedelta


def test_list_with_due_problem(mock_data, console):
    problem = "Due Problem"
    # Add problem with rating=1, then backdate it so it's due
    args = SimpleNamespace(name=problem, rating=1)
    add.handle(args=args, console=console)

    with open(mock_data.PROGRESS_FILE) as f:
        data = json.load(f)
    data[problem]["history"][-1]["date"] = (
        datetime.now() - timedelta(days=2)
    ).isoformat()
    with open(mock_data.PROGRESS_FILE, "w") as f:
        json.dump(data, f)

    args = SimpleNamespace(n=None)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "Problems to Practice Today" in output
    assert problem in output


def test_list_with_next_up_fallback(mock_data, console):
    problem = "Next Up Problem"
    args = SimpleNamespace(action="add", name=problem)
    nextup.handle(args=args, console=console)

    args = SimpleNamespace(n=None)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert problem in output
    assert "Problems to Practice Today" in output
    assert "No problems due" not in output


def test_list_empty(console):
    args = SimpleNamespace(n=None)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "No problems due today or in Next Up" in output


def test_should_audit_probability(monkeypatch):
    monkeypatch.setattr(list_, "load_json", lambda _: {"audit_probability": 1.0})
    monkeypatch.setattr(list_.random, "random", lambda: 0.0)  # force audit
    assert list_.should_audit() is True

    monkeypatch.setattr(list_, "load_json", lambda _: {"audit_probability": 0.0})
    monkeypatch.setattr(list_.random, "random", lambda: 1.0)  # force no audit
    assert list_.should_audit() is False
