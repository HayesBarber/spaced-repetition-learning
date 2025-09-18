from srl.commands import inprogress, add
from types import SimpleNamespace


def test_inprogress_with_items(mock_data, console, load_json):
    problem_a = "Problem A"
    problem_b = "Problem B"

    args = SimpleNamespace(name=problem_a, rating=5)
    add.handle(args, console)

    args = SimpleNamespace(name=problem_b, rating=4)
    add.handle(args, console)

    args = SimpleNamespace()
    inprogress.handle(args, console)

    data = load_json(mock_data.PROGRESS_FILE)

    output = console.export_text()
    assert "Problems in Progress" in output
    assert problem_a in output
    assert problem_a in data
    assert problem_b in output
    assert problem_b in data


def test_inprogress_empty(console):
    args = SimpleNamespace()
    inprogress.handle(args=args, console=console)

    output = console.export_text()
    assert "No problems currently in progress" in output
