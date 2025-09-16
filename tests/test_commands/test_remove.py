from srl.commands import remove, add
import json
from types import SimpleNamespace


def test_remove_existing_problem(mock_data, console):
    problem = "Test Problem"
    rating = 3
    args = SimpleNamespace(name=problem, rating=rating)
    add.handle(args, console)

    args = SimpleNamespace(name=problem)
    remove.handle(args=args, console=console)

    with open(mock_data.PROGRESS_FILE) as f:
        data = json.load(f)
    assert problem not in data

    output = console.export_text()
    assert "Removed" in output
    assert problem in output


def test_remove_nonexistent_problem(mock_data, console):
    problem = "Nonexistent Problem"
    args = SimpleNamespace(name=problem)

    remove.handle(args=args, console=console)

    with open(mock_data.PROGRESS_FILE) as f:
        data = json.load(f)
    assert problem not in data

    output = console.export_text()
    assert "not found in in-progress" in output
    assert problem in output
