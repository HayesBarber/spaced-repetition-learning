from srl.commands import remove, add
from types import SimpleNamespace
import pytest


def test_remove_existing_problem(mock_data, load_json, console):
    problem = "Test Problem"
    rating = 3
    args = SimpleNamespace(name=problem, rating=rating)
    add.handle(args, console)

    args = SimpleNamespace(name=problem)
    remove.handle(args=args, console=console)

    data = load_json(mock_data.PROGRESS_FILE)
    assert problem not in data

    output = console.export_text()
    assert "Removed" in output
    assert problem in output


def test_remove_nonexistent_problem(mock_data, load_json, console):
    problem = "Nonexistent Problem"
    args = SimpleNamespace(name=problem)

    remove.handle(args=args, console=console)

    data = load_json(mock_data.PROGRESS_FILE)
    assert problem not in data

    output = console.export_text()
    assert "not found in in-progress" in output
    assert problem in output


def test_remove_by_number(load_json, mock_data, console):
    add.handle(SimpleNamespace(name="A", rating=5, number=None), console)
    add.handle(SimpleNamespace(name="B", rating=5, number=None), console)

    args = SimpleNamespace(name=None, number=2)
    remove.handle(args=args, console=console)

    data = load_json(mock_data.PROGRESS_FILE)

    assert "B" not in data
    assert "A" in data

    output = console.export_text()
    assert "Removed" in output
    assert "B" in output


@pytest.mark.parametrize("num", [0, -1, 5])
def test_remove_by_number_out_of_range(mock_data, load_json, console, num):
    add.handle(SimpleNamespace(name="X", rating=2), console)

    args = SimpleNamespace(name=None, number=num)
    remove.handle(args=args, console=console)

    data = load_json(mock_data.PROGRESS_FILE)

    assert "X" in data
    output = console.export_text()
    assert "Invalid problem number" in output
