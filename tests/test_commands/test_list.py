from srl.commands import list_, add, nextup
from types import SimpleNamespace


def test_list_with_due_problem(console, monkeypatch, backdate_problem):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Due Problem"
    # Add problem with rating=1, then backdate it so it's due
    args = SimpleNamespace(name=problem, rating=1)
    add.handle(args=args, console=console)
    backdate_problem(problem, 2)

    args = SimpleNamespace(n=None)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "Problems to Practice Today (1)" in output
    assert problem in output


def test_list_with_next_up_fallback(console, monkeypatch):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Next Up Problem"
    args = SimpleNamespace(action="add", name=problem)
    nextup.handle(args=args, console=console)

    args = SimpleNamespace(n=None)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert problem in output
    assert "Problems to Practice Today" in output
    assert "No problems due" not in output


def test_list_empty(console, monkeypatch):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

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


def test_list_triggers_audit(mock_data, console, monkeypatch):
    problem = "Audit Problem"
    args = SimpleNamespace(name=problem, rating=5)
    add.handle(args=args, console=console)
    add.handle(args=args, console=console)  # move to mastered

    monkeypatch.setattr(list_, "should_audit", lambda: True)

    args = SimpleNamespace(n=None)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "You have been randomly audited!" in output
    assert "Audit problem:" in output
    assert problem in output
