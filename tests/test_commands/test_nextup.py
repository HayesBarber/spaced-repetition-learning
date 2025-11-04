from srl.commands import nextup
from types import SimpleNamespace


def test_add_to_next_up_new_problem(mock_data, console, load_json):
    problem = "What is the square root of 16?"
    args = SimpleNamespace(action="add", name=problem)

    nextup.handle(args=args, console=console)

    data = load_json(mock_data.NEXT_UP_FILE)
    assert problem in data

    output = console.export_text()
    assert "Added" in output
    assert problem in output


def test_add_to_next_up_duplicate(console):
    problem = "Duplicate Problem"
    args = SimpleNamespace(action="add", name=problem)

    # First add
    nextup.handle(args=args, console=console)
    # Second add (duplicate)
    nextup.handle(args=args, console=console)

    output = console.export_text()
    assert f'"{problem}" is already in the Next Up queue.' in output


def test_add_to_next_up_without_name(console):
    args = SimpleNamespace(action="add", name=None)

    nextup.handle(args=args, console=console)

    output = console.export_text()
    assert "Please provide a problem name" in output


def test_list_next_up_with_items(console):
    problem = "Integration test problem"
    args_add = SimpleNamespace(action="add", name=problem)
    nextup.handle(args=args_add, console=console)

    args_list = SimpleNamespace(action="list")
    nextup.handle(args=args_list, console=console)

    output = console.export_text()
    assert "Next Up Problems (1)" in output
    assert problem in output


def test_list_next_up_empty(console):
    args = SimpleNamespace(action="list")
    nextup.handle(args=args, console=console)

    output = console.export_text()
    assert "Next Up queue is empty" in output


def test_remove_from_next_up(mock_data, console, load_json):
    problem = "Removable problem"
    args_add = SimpleNamespace(action="add", name=problem)
    nextup.handle(args=args_add, console=console)

    args_remove = SimpleNamespace(action="remove", name=problem)
    nextup.handle(args=args_remove, console=console)

    data = load_json(mock_data.NEXT_UP_FILE)
    assert problem not in data

    output = console.export_text()
    assert "Removed" in output
    assert problem in output


def test_clear_next_up(mock_data, console, load_json):
    p1 = "Problem A"
    p2 = "Problem B"
    nextup.handle(args=SimpleNamespace(action="add", name=p1), console=console)
    nextup.handle(args=SimpleNamespace(action="add", name=p2), console=console)

    nextup.handle(args=SimpleNamespace(action="clear"), console=console)

    data = load_json(mock_data.NEXT_UP_FILE)
    assert data == {}

    output = console.export_text()
    assert "Next Up queue cleared" in output
