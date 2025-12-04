from srl.commands import audit, add
from types import SimpleNamespace


def test_start_audit_with_no_mastered(console):
    args = SimpleNamespace(audit_pass=False, audit_fail=False)
    audit.handle(args=args, console=console)

    output = console.export_text()
    assert "No mastered problems available for audit" in output


def test_start_audit_with_mastered(console):
    problem = "Mastered Problem"
    rating = 5
    args = SimpleNamespace(name=problem, rating=rating)

    add.handle(args=args, console=console)
    add.handle(args=args, console=console)

    args = SimpleNamespace(audit_pass=False, audit_fail=False)
    audit.handle(args=args, console=console)

    output = console.export_text()
    assert "You are now being audited on" in output
    assert problem in output


def test_show_current_audit(console):
    problem = "Current Audit"
    rating = 5
    args = SimpleNamespace(name=problem, rating=rating)

    add.handle(args=args, console=console)
    add.handle(args=args, console=console)

    args = SimpleNamespace(audit_pass=False, audit_fail=False)
    audit.handle(args=args, console=console)
    # second call should just show current audit
    audit.handle(args=args, console=console)

    output = console.export_text()
    assert "Current audit problem" in output
    assert problem in output
    assert "Run with --pass or --fail" in output


def test_pass_current_audit(console, mock_data, dump_json, load_json):
    problem = "Audit Pass Problem"
    dump_json(mock_data.AUDIT_FILE, {"current_audit": problem})

    args = SimpleNamespace(audit_pass=True, audit_fail=False)
    audit.handle(args=args, console=console)

    data = load_json(mock_data.AUDIT_FILE)
    assert "current_audit" not in data
    assert any(entry["result"] == "pass" for entry in data.get("history", []))

    output = console.export_text()
    assert "Audit passed!" in output


def test_fail_current_audit(console, mock_data, dump_json, load_json):
    problem = "Audit Fail Problem"
    dump_json(mock_data.MASTERED_FILE, {problem: {"history": [{"rating": 5}]}})
    dump_json(mock_data.AUDIT_FILE, {"current_audit": problem})

    args = SimpleNamespace(audit_pass=False, audit_fail=True)
    audit.handle(args=args, console=console)

    mastered = load_json(mock_data.MASTERED_FILE)
    progress = load_json(mock_data.PROGRESS_FILE)
    audit_data = load_json(mock_data.AUDIT_FILE)

    assert problem not in mastered
    assert problem in progress
    assert any(entry["result"] == "fail" for entry in audit_data.get("history", []))

    output = console.export_text()
    assert "Audit failed." in output
    assert "moved back to in-progress" in output


def test_fail_audit_with_nonexistent_problem(console, mock_data, dump_json):
    problem = "Missing Problem"
    dump_json(mock_data.AUDIT_FILE, {"current_audit": problem})

    args = SimpleNamespace(audit_pass=False, audit_fail=True)
    audit.handle(args=args, console=console)

    output = console.export_text()
    assert f"{problem}" in output
    assert "not found in mastered" in output
