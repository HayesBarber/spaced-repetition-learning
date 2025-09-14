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
    assert f"Added rating {rating} for '{problem}'"


def test_move_problem_to_mastered(mock_data, console):
    problem = "What is the capital of France?"
    rating = 5
    progress_file = mock_data.PROGRESS_FILE
    mastered_file = mock_data.MASTERED_FILE
    progress_file.write_text(
        json.dumps({problem: {"history": [{"rating": 5, "date": "2024-06-01"}]}})
    )
    mastered_file.write_text(json.dumps({}))

    args = SimpleNamespace(name=problem, rating=rating)
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
    progress_file = mock_data.PROGRESS_FILE
    next_up_file = mock_data.NEXT_UP_FILE

    next_up_file.write_text(json.dumps({problem: {"dummy": True}}))
    progress_file.write_text(json.dumps({}))

    args = SimpleNamespace(name=problem, rating=rating)
    add.handle(args=args, console=console)

    with open(next_up_file) as f:
        next_up = json.load(f)
    assert problem not in next_up

    output = console.export_text()
    assert "Added rating" in output
