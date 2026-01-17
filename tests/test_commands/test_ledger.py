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


def test_ledger_count_flag_displays_count_only(console, mock_data, dump_json):
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

    args = SimpleNamespace(count=True)
    ledger.handle(args=args, console=console)

    output = console.export_text()
    assert "Total attempts: 3" in output
    assert "two-sum" not in output
    assert "valid-parentheses" not in output
    assert "merge-sorted-array" not in output


def test_ledger_count_flag_with_no_data(console):
    args = SimpleNamespace(count=True)
    ledger.handle(args=args, console=console)

    output = console.export_text()
    assert "Total attempts: 0" in output


def test_ledger_audit_failure_double_counting(console, mock_data, dump_json):
    """
    Test that failed audits are not double-counted in the ledger.

    When an audit fails:
    1. An audit fail entry is added to AUDIT_FILE
    2. The problem is moved to PROGRESS_FILE with a new history entry (rating: 1)

    The ledger should only count the progress entry, not both.
    This test will initially fail (exposing the bug) and be updated after the fix.
    """
    problem = "two-sum"
    fail_date = "2025-01-15"

    audit_data = {
        "history": [{"date": fail_date, "problem": problem, "result": "fail"}]
    }
    dump_json(mock_data.AUDIT_FILE, audit_data)

    progress_data = {
        problem: {
            "history": [
                {"rating": 5, "date": "2025-01-10"},
                {"rating": 5, "date": "2025-01-12"},
                {"rating": 1, "date": fail_date},
            ]
        }
    }
    dump_json(mock_data.PROGRESS_FILE, progress_data)

    args = SimpleNamespace()
    ledger.handle(args=args, console=console)

    output = console.export_text()

    problem_occurrences = output.count(problem)
    fail_date_occurrences = output.count(fail_date)

    assert (
        fail_date_occurrences == 1
    ), f"Expected 1 occurrence of {fail_date}, got {fail_date_occurrences}"
    assert (
        problem_occurrences == 3
    ), f"Expected 3 total occurrences of {problem} (2 initial + 1 after fail), got {problem_occurrences}"
