from srl.commands import add
import json
from types import SimpleNamespace


def test_add_new_problem(mock_data, console):
    problem = "What is 2+2?"
    rating = 3
    args = SimpleNamespace(name=problem, rating=rating)

    add.handle(
        args=args,
        console=console,
    )

    progress_file = mock_data.PROGRESS_FILE
    with open(progress_file) as f:
        progress = json.load(f)
    assert problem in progress
    assert progress[problem]["history"][0]["rating"] == rating

    output = console.export_text()
    assert f"Added rating {rating} for '{problem}'" in output


def test_move_problem_to_mastered(mock_data, console):
    problem = "What is the capital of France?"
    rating = 5
    progress_file = mock_data.PROGRESS_FILE
    mastered_file = mock_data.MASTERED_FILE

    args = SimpleNamespace(name=problem, rating=rating)
    # call twice with rating 5
    add.handle(args=args, console=console)
    add.handle(args=args, console=console)

    with open(progress_file) as f:
        progress = json.load(f)
    assert problem not in progress

    with open(mastered_file) as f:
        mastered = json.load(f)
    assert problem in mastered
    assert mastered[problem]["history"][-1]["rating"] == rating

    output = console.export_text()
    assert "moved to" in output


def test_remove_problem_from_next_up(mock_data, console):
    problem = "What is the speed of light?"
    rating = 4
    next_up_file = mock_data.NEXT_UP_FILE

    next_up_file.write_text(json.dumps({problem: {"dummy": True}}))

    args = SimpleNamespace(name=problem, rating=rating)
    add.handle(args=args, console=console)

    with open(next_up_file) as f:
        next_up = json.load(f)
    assert problem not in next_up

    output = console.export_text()
    assert "Added rating" in output


def test_append_to_mastered_already_present(mock_data, console):
    problem = "Existing mastered problem"
    rating = 5
    progress_file = mock_data.PROGRESS_FILE
    mastered_file = mock_data.MASTERED_FILE

    # Pre-populate MASTERED_FILE with existing history
    initial_history = [{"rating": 5, "date": "2025-11-14"}]
    mastered_file.write_text(json.dumps({problem: {"history": initial_history.copy()}}))

    # Pre-populate PROGRESS_FILE with the problem, enough to trigger mastery
    progress_file.write_text(
        json.dumps({problem: {"history": [{"rating": 5, "date": "2025-11-15"}]}})
    )

    args = SimpleNamespace(name=problem, rating=rating)
    add.handle(args=args, console=console)

    # Check PROGRESS_FILE no longer contains the problem
    with open(progress_file) as f:
        progress = json.load(f)
    assert problem not in progress

    # Check MASTERED_FILE history appended
    with open(mastered_file) as f:
        mastered = json.load(f)
    assert problem in mastered
    # Should contain initial + two new entries
    assert len(mastered[problem]["history"]) == len(initial_history) + 2
    assert mastered[problem]["history"][: len(initial_history)] == initial_history

    output = console.export_text()
    assert "moved to" in output
