from srl.commands import ledger, add
from types import SimpleNamespace


def test_ledger_empty_data_displays_nothing(console):
    args = SimpleNamespace()

    ledger.handle(args=args, console=console)

    output = console.export_text()
    assert len(output.strip()) == 0


def test_ledger_with_mixed_data_sources(console, mock_data, dump_json):
    progress_data = {"two-sum": {"history": [{"rating": 3, "date": "2025-01-15"}]}}
    dump_json(mock_data.PROGRESS_FILE, progress_data)

    mastered_data = {
        "valid-parentheses": {"history": [{"rating": 5, "date": "2025-01-14"}]}
    }
    dump_json(mock_data.MASTERED_FILE, mastered_data)

    audit_data = {
        "history": [
            {
                "date": "2025-01-13",
                "problem": "merge-sorted-array",
                "result": "pass",
            }
        ]
    }
    dump_json(mock_data.AUDIT_FILE, audit_data)

    args = SimpleNamespace()
    ledger.handle(args=args, console=console)

    output = console.export_text()
    assert "two-sum" in output
    assert "valid-parentheses" in output
    assert "merge-sorted-array" in output


def test_ledger_audit_pass_converts_to_rating_5(console, mock_data, dump_json):
    audit_data = {
        "history": [
            {
                "date": "2025-01-15",
                "problem": "two-sum",
                "result": "pass",
            },
            {
                "date": "2025-01-14",
                "problem": "valid-parentheses",
                "result": "fail",
            },
        ]
    }
    dump_json(mock_data.AUDIT_FILE, audit_data)

    args = SimpleNamespace()
    ledger.handle(args=args, console=console)

    output = console.export_text()
    assert " 5 " in output
    assert " 1 " in output


def test_ledger_data_sorted_chronologically(console, mock_data, dump_json):
    audit_data = {
        "history": [
            {
                "date": "2025-01-15",
                "problem": "three-sum",
                "result": "pass",
            },
            {
                "date": "2025-01-13",
                "problem": "valid-parentheses",
                "result": "fail",
            },
            {
                "date": "2025-01-14",
                "problem": "two-sum",
                "result": "pass",
            },
        ]
    }
    dump_json(mock_data.AUDIT_FILE, audit_data)

    args = SimpleNamespace()
    ledger.handle(args=args, console=console)

    output = console.export_text()
    lines = output.strip().split("\n")
    date_lines = [line for line in lines if "2025-01-" in line]
    assert "2025-01-13" in date_lines[0]
    assert "2025-01-14" in date_lines[1]
    assert "2025-01-15" in date_lines[2]


def test_ledger_after_adding_progress_attempt(console):
    problem = "two-sum"
    rating = 4
    args = SimpleNamespace(name=problem, rating=rating)
    add.handle(args=args, console=console)

    console.clear()

    ledger_args = SimpleNamespace()
    ledger.handle(args=ledger_args, console=console)

    output = console.export_text()
    assert "two-sum" in output
    assert " 4 " in output
    assert "progress" in output

