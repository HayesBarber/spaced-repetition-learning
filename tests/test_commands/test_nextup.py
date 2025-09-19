from srl.commands import nextup
import json
from types import SimpleNamespace


def test_add_to_next_up_new_problem(mock_data, console):
    problem = "What is the square root of 16?"
    args = SimpleNamespace(action="add", name=problem)

    nextup.handle(args=args, console=console)

    with open(mock_data.NEXT_UP_FILE) as f:
        data = json.load(f)
    assert problem in data

    output = console.export_text()
    assert "Added" in output
    assert problem in output


def test_add_to_next_up_duplicate(mock_data, console):
    problem = "Duplicate Problem"
    args = SimpleNamespace(action="add", name=problem)

    # First add
    nextup.handle(args=args, console=console)
    # Second add (duplicate)
    nextup.handle(args=args, console=console)

    output = console.export_text()
    assert f'"{problem}" is already in the Next Up queue.' in output


def test_add_to_next_up_without_name(mock_data, console):
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
