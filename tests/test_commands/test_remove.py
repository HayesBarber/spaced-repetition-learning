from srl.commands import remove, add
from types import SimpleNamespace


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


def test_remove_by_number(load_json, backdate_problem, mock_data, console):
    problem_a = "A"
    add.handle(SimpleNamespace(name=problem_a, rating=5, number=None), console)
    backdate_problem(problem_a, 5)
    problem_b = "B"
    add.handle(SimpleNamespace(name=problem_b, rating=5, number=None), console)
    backdate_problem(problem_b, 5)

    args = SimpleNamespace(name=None, number=2)
    remove.handle(args=args, console=console)

    data = load_json(mock_data.PROGRESS_FILE)

    assert "B" not in data
    assert "A" in data

    output = console.export_text()
    assert "Removed" in output
    assert "B" in output
