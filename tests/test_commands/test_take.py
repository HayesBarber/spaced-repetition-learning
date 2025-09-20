from srl.commands import take, nextup
from types import SimpleNamespace


def test_take_print_problem(console):
    problem1 = "Problem 1"
    problem2 = "Problem 2"
    nextup.handle(SimpleNamespace(action="add", name=problem1), console=console)
    nextup.handle(SimpleNamespace(action="add", name=problem2), console=console)

    args = SimpleNamespace(index=0, action=None, rating=None)
    take.handle(args=args, console=console)
    output = console.export_text()
    assert problem1 in output


def test_take_add_problem_with_rating(console, load_json, mock_data):
    problem = "Problem with rating"
    nextup.handle(SimpleNamespace(action="add", name=problem), console=console)

    args = SimpleNamespace(index=0, action="add", rating=3)
    take.handle(args=args, console=console)

    inprogress_data = load_json(mock_data.PROGRESS_FILE)
    assert problem in inprogress_data
    assert inprogress_data[problem]["history"][-1]["rating"] == 3

    nextup_data = load_json(mock_data.NEXT_UP_FILE)
    assert problem not in nextup_data


def test_take_add_missing_rating(console):
    problem = "Problem missing rating"
    nextup.handle(SimpleNamespace(action="add", name=problem), console=console)

    args = SimpleNamespace(index=0, action="add", rating=None)
    take.handle(args=args, console=console)
    output = console.export_text()
    assert "Error: rating must be provided" in output


def test_take_index_out_of_bounds(console):
    args = SimpleNamespace(index=5, action=None, rating=None)
    take.handle(args=args, console=console)
    output = console.export_text()
    assert output == ""
