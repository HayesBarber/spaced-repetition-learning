from srl.commands import nextup
from types import SimpleNamespace
import shutil
from pathlib import Path
import pytest


@pytest.fixture
def blind75_file(tmp_path):
    src = Path("starter_data/blind_75.txt")
    dst = tmp_path / "blind_75.txt"
    shutil.copy(src, dst)
    return dst


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


def test_nextup_add_file_all_new(blind75_file, console, mock_data, load_json):
    args = SimpleNamespace(action="add", file=str(blind75_file))
    nextup.handle(args=args, console=console)

    data = load_json(mock_data.NEXT_UP_FILE)
    assert len(data) == 75

    output = console.export_text()
    assert "Added 75 problems from file" in output


def test_nextup_add_file_some_existing(blind75_file, console, mock_data, load_json):
    args = SimpleNamespace(action="add", file=str(blind75_file))

    # First add: all 75 problems
    nextup.handle(args=args, console=console)

    # Capture console output
    console.clear()

    # Second add: all problems already exist
    nextup.handle(args=args, console=console)

    data = load_json(mock_data.NEXT_UP_FILE)
    # Should still have 75 problems
    assert len(data) == 75

    output = console.export_text()
    # No new problems should be added on second pass
    assert "Added 0 problems from file" in output


def test_nextup_add_file_not_found(console, mock_data, load_json):
    args = SimpleNamespace(action="add", file="non_existent_file.txt")

    nextup.handle(args=args, console=console)

    data = load_json(mock_data.NEXT_UP_FILE)
    # Queue should remain empty
    assert len(data) == 0

    output = console.export_text()
    assert "File not found" in output


def test_nextup_add_file_ignores_blank_lines(tmp_path, console, mock_data, load_json):
    # Create a file with 3 problems and 2 blank lines
    file_path = tmp_path / "test_blank_lines.txt"
    content = "\nProblem 1\n\nProblem 2\nProblem 3\n\n"
    file_path.write_text(content)

    args = SimpleNamespace(action="add", file=str(file_path))
    nextup.handle(args=args, console=console)

    data = load_json(mock_data.NEXT_UP_FILE)
    # Only 3 problems should be added
    assert len(data) == 3
    assert "Problem 1" in data
    assert "Problem 2" in data
    assert "Problem 3" in data

    output = console.export_text()
    assert "Added 3 problems from file" in output


def test_nextup_add_file_mixed_whitespace(tmp_path, console, mock_data, load_json):
    # File with problems that have leading/trailing whitespace
    file_path = tmp_path / "test_whitespace.txt"
    content = "   Problem A\nProblem B   \n  Problem C  \n"
    file_path.write_text(content)

    args = SimpleNamespace(action="add", file=str(file_path))
    nextup.handle(args=args, console=console)

    data = load_json(mock_data.NEXT_UP_FILE)
    # All three problems should be added with whitespace stripped
    assert len(data) == 3
    assert "Problem A" in data
    assert "Problem B" in data
    assert "Problem C" in data

    output = console.export_text()
    assert "Added 3 problems from file" in output


def test_add_to_next_up_problem_already_inprogress(
    mock_data, console, dump_json, load_json
):
    # Simulate a problem that is already in progress
    problem = "In Progress Problem"
    in_progress_file = mock_data.PROGRESS_FILE
    initial_history = [{"rating": 5, "date": "2025-11-14"}]
    dump_json(in_progress_file, {problem: {"history": initial_history.copy()}})

    args = SimpleNamespace(action="add", name=problem)
    nextup.handle(args=args, console=console)

    # Should not add because it's already in-progress
    next_up_file = mock_data.NEXT_UP_FILE
    data = load_json(next_up_file)
    assert problem not in data
    output = console.export_text()
    assert f'"{problem}" is already in progress' in output

    console.clear()

    # Call again with allow mastered flag
    args = SimpleNamespace(action="add", name=problem, allow_mastered=True)
    nextup.handle(args=args, console=console)

    # Should not add even with allow mastered
    data = load_json(next_up_file)
    assert problem not in data
    output = console.export_text()
    assert f'"{problem}" is already in progress' in output


def test_add_to_next_up_problem_already_in_mastered(
    mock_data, console, dump_json, load_json
):
    # Simulate a problem that is already mastered
    problem = "Mastered Problem"
    initial_history = [{"rating": 5, "date": "2025-11-14"}]
    mastered_file = mock_data.MASTERED_FILE
    dump_json(mastered_file, {problem: {"history": initial_history.copy()}})

    args = SimpleNamespace(action="add", name=problem)
    nextup.handle(args=args, console=console)

    # Should not add because it's already mastered
    next_up_file = mock_data.NEXT_UP_FILE
    data = load_json(next_up_file)
    assert problem not in data
    output = console.export_text()
    assert f'"{problem}" is already mastered' in output


def test_add_to_next_up_problem_already_in_mastered_allow_mastered(
    mock_data, console, dump_json, load_json
):
    # Simulate a problem that is already mastered
    problem = "Mastered Problem"
    initial_history = [{"rating": 5, "date": "2025-11-14"}]
    mastered_file = mock_data.MASTERED_FILE
    dump_json(mastered_file, {problem: {"history": initial_history.copy()}})

    args = SimpleNamespace(action="add", name=problem, allow_mastered=True)
    nextup.handle(args=args, console=console)

    # Should add because we passed allow_mastered
    next_up_file = mock_data.NEXT_UP_FILE
    data = load_json(next_up_file)
    assert problem in data
    output = console.export_text()
    assert f'"{problem}" is mastered but will be added due to flag.' in output
