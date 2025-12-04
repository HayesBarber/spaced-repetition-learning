from srl.commands import add, nextup
from types import SimpleNamespace


def test_add_new_problem(mock_data, console, load_json):
    problem = "What is 2+2?"
    rating = 3
    args = SimpleNamespace(name=problem, rating=rating)

    add.handle(
        args=args,
        console=console,
    )

    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert problem in progress
    assert progress[problem]["history"][0]["rating"] == rating

    output = console.export_text()
    assert f"Added rating {rating} for '{problem}'" in output


def test_move_problem_to_mastered(mock_data, console, load_json):
    problem = "What is the capital of France?"
    rating = 5
    progress_file = mock_data.PROGRESS_FILE
    mastered_file = mock_data.MASTERED_FILE

    args = SimpleNamespace(name=problem, rating=rating)
    # call twice with rating 5
    add.handle(args=args, console=console)
    add.handle(args=args, console=console)

    progress = load_json(progress_file)
    assert problem not in progress

    mastered = load_json(mastered_file)
    assert problem in mastered
    assert mastered[problem]["history"][-1]["rating"] == rating

    output = console.export_text()
    assert "moved to" in output


def test_remove_problem_from_next_up(mock_data, console, load_json, dump_json):
    problem = "What is the speed of light?"
    rating = 4
    next_up_file = mock_data.NEXT_UP_FILE

    dump_json(next_up_file, {problem: {"dummy": True}})

    args = SimpleNamespace(name=problem, rating=rating)
    add.handle(args=args, console=console)

    next_up = load_json(next_up_file)
    assert problem not in next_up

    output = console.export_text()
    assert "Added rating" in output


def test_append_to_mastered_already_present(mock_data, console, load_json, dump_json):
    problem = "Existing mastered problem"
    rating = 5
    progress_file = mock_data.PROGRESS_FILE
    mastered_file = mock_data.MASTERED_FILE

    # Pre-populate MASTERED_FILE with existing history
    initial_history = [{"rating": 5, "date": "2025-11-14"}]
    dump_json(mastered_file, {problem: {"history": initial_history.copy()}})

    # Pre-populate PROGRESS_FILE with the problem, enough to trigger mastery
    dump_json(
        progress_file, {problem: {"history": [{"rating": 5, "date": "2025-11-15"}]}}
    )

    args = SimpleNamespace(name=problem, rating=rating)
    add.handle(args=args, console=console)

    # Check PROGRESS_FILE no longer contains the problem
    progress = load_json(progress_file)
    assert problem not in progress

    # Check MASTERED_FILE history appended
    mastered = load_json(mastered_file)
    assert problem in mastered
    # Should contain initial + two new entries
    assert len(mastered[problem]["history"]) == len(initial_history) + 2
    assert mastered[problem]["history"][: len(initial_history)] == initial_history

    output = console.export_text()
    assert "moved to" in output


def test_add_by_number_valid(console, load_json, backdate_problem, mock_data):
    problem1 = "Problem 1"
    problem2 = "Problem 2"

    # Add problems and make them due
    add.handle(SimpleNamespace(name=problem1, rating=3, number=None), console)
    backdate_problem(problem1, 5)
    add.handle(SimpleNamespace(name=problem2, rating=3, number=None), console)
    backdate_problem(problem2, 5)

    console.clear()

    # Add a rating to the second problem
    rating = 4
    args = SimpleNamespace(number=2, rating=rating, name=None)
    add.handle(args, console)

    progress_data = load_json(mock_data.PROGRESS_FILE)
    assert problem2 in progress_data
    assert progress_data[problem2]["history"][-1]["rating"] == rating

    output = console.export_text()
    assert f"Added rating {rating} for '{problem2}'" in output


def test_add_by_number_invalid_too_high(console, backdate_problem):
    problem1 = "Problem 1"

    # Add a problem and make it due
    add.handle(SimpleNamespace(name=problem1, rating=3, number=None), console)
    backdate_problem(problem1, 5)

    console.clear()

    # Try to add a rating to a problem that doesn't exist
    args = SimpleNamespace(number=2, rating=4, name=None)
    add.handle(args, console)

    output = console.export_text()
    assert "Invalid problem number: 2" in output


def test_add_by_number_invalid_zero(console, backdate_problem):
    problem1 = "Problem 1"

    # Add a problem and make it due
    add.handle(SimpleNamespace(name=problem1, rating=3, number=None), console)
    backdate_problem(problem1, 5)

    console.clear()

    # Try to add a rating with number 0
    args = SimpleNamespace(number=0, rating=4, name=None)
    add.handle(args, console)

    output = console.export_text()
    assert "Invalid problem number: 0" in output


def test_add_by_number_no_due_problems(console):
    # Try to add a rating when no problems are due
    args = SimpleNamespace(number=1, rating=4, name=None)
    add.handle(args, console)

    output = console.export_text()
    assert "Invalid problem number: 1" in output


def test_add_by_number_removes_from_nextup(console, load_json, mock_data):
    problem = "Problem from nextup"
    nextup.handle(SimpleNamespace(action="add", name=problem, file=None, allow_mastered=False), console)

    console.clear()

    # Add a rating to the problem from nextup
    rating = 4
    args = SimpleNamespace(number=1, rating=rating, name=None)
    add.handle(args, console)

    progress_data = load_json(mock_data.PROGRESS_FILE)
    assert problem in progress_data
    assert progress_data[problem]["history"][-1]["rating"] == rating

    nextup_data = load_json(mock_data.NEXT_UP_FILE)
    assert problem not in nextup_data

    output = console.export_text()
    assert f"Added rating {rating} for '{problem}'" in output


def test_add_by_number_mastery(console, load_json, backdate_problem, mock_data):
    problem = "Problem to be mastered"
    add.handle(SimpleNamespace(name=problem, rating=5, number=None), console)
    backdate_problem(problem, 5)

    console.clear()

    args = SimpleNamespace(number=1, rating=5, name=None)
    add.handle(args, console)

    progress_data = load_json(mock_data.PROGRESS_FILE)
    assert problem not in progress_data

    mastered_data = load_json(mock_data.MASTERED_FILE)
    assert problem in mastered_data

    output = console.export_text()
    assert f"{problem} moved to mastered!" in output


def test_add_by_number_case_insensitive(console, load_json, backdate_problem, mock_data):
    problem_lower = "problem"
    problem_upper = "Problem"

    # Add with lowercase name, make it due
    add.handle(SimpleNamespace(name=problem_lower, rating=3, number=None), console)
    backdate_problem(problem_lower, 5)

    console.clear()

    # `get_due_problems` should return "problem". `add -n 1` should update the same entry.
    # We will pretend that `get_due_problems()` returned "Problem" (with capital P)
    # to test the case-insensitivity of the `add` command.
    from srl.commands.list_ import get_due_problems
    original_get_due_problems = get_due_problems
    def mock_get_due_problems():
        return [problem_upper]
    
    add.get_due_problems = mock_get_due_problems

    args = SimpleNamespace(number=1, rating=4, name=None)
    add.handle(args, console)

    # restore original function
    add.get_due_problems = original_get_due_problems

    progress_data = load_json(mock_data.PROGRESS_FILE)
    assert problem_lower in progress_data
    assert problem_upper not in progress_data
    assert len(progress_data[problem_lower]["history"]) == 2
    assert progress_data[problem_lower]["history"][-1]["rating"] == 4
