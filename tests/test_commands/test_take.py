from srl.commands import take, nextup, add
from types import SimpleNamespace


def test_take_print_problem(console):
    problem1 = "Problem 1"
    problem2 = "Problem 2"
    nextup.handle(SimpleNamespace(action="add", name=problem1), console=console)
    nextup.handle(SimpleNamespace(action="add", name=problem2), console=console)

    args = SimpleNamespace(index=1, action=None, rating=None)
    take.handle(args=args, console=console)
    output = console.export_text()
    assert problem1 in output


def test_take_add_problem_from_inprogress(
    console, load_json, backdate_problem, mock_data
):
    problem = "Problem with rating"
    args = SimpleNamespace(name=problem, rating=4)
    add.handle(args, console)

    # backdate problem so it's due
    backdate_problem(problem, 5)

    new_rating = 3
    args = SimpleNamespace(index=1, action="add", rating=new_rating)
    take.handle(args=args, console=console)

    inprogress_data = load_json(mock_data.PROGRESS_FILE)
    assert problem in inprogress_data
    assert inprogress_data[problem]["history"][-1]["rating"] == new_rating


def test_take_add_problem_from_nextup(console, load_json, mock_data):
    problem = "Problem with rating"
    nextup.handle(SimpleNamespace(action="add", name=problem), console=console)

    args = SimpleNamespace(index=1, action="add", rating=3)
    take.handle(args=args, console=console)

    inprogress_data = load_json(mock_data.PROGRESS_FILE)
    assert problem in inprogress_data
    assert inprogress_data[problem]["history"][-1]["rating"] == 3

    nextup_data = load_json(mock_data.NEXT_UP_FILE)
    assert problem not in nextup_data


def test_take_add_missing_rating(console):
    problem = "Problem missing rating"
    nextup.handle(SimpleNamespace(action="add", name=problem), console=console)

    args = SimpleNamespace(index=1, action="add", rating=None)
    take.handle(args=args, console=console)

    output = console.export_text()
    assert "Error: rating must be provided" in output


def test_take_index_out_of_bounds_high(console):
    # Add a problem directly to NEXT_UP_FILE
    from srl.storage import save_json, NEXT_UP_FILE
    from srl.utils import today
    save_json(NEXT_UP_FILE, {"Problem A": {"added": today().isoformat()}})

    args = SimpleNamespace(index=2, action=None, rating=None) # Index 2 for 1 problem is out of bounds
    take.handle(args=args, console=console)
    output = console.export_text()
    assert output == ""


def test_take_index_zero_is_invalid(console):
    # Add a problem directly to NEXT_UP_FILE
    from srl.storage import save_json, NEXT_UP_FILE
    from srl.utils import today
    save_json(NEXT_UP_FILE, {"Problem B": {"added": today().isoformat()}})

    args = SimpleNamespace(index=0, action=None, rating=None) # Index 0 should be invalid
    take.handle(args=args, console=console)
    output = console.export_text()
    assert output == ""


def test_take_add_no_problems_due(console, load_json, mock_data):
    problem = "Problem with rating"
    original_rating = 4
    args = SimpleNamespace(name=problem, rating=original_rating)
    add.handle(args, console)

    # the problem ^ just added is not due, so "take" should do nothing
    new_rating = 3
    args = SimpleNamespace(index=1, action="add", rating=new_rating)
    take.handle(args=args, console=console)

    inprogress_data = load_json(mock_data.PROGRESS_FILE)
    assert problem in inprogress_data
    assert inprogress_data[problem]["history"][-1]["rating"] == original_rating


def test_take_print_url_from_due_problem(console, backdate_problem):
    problem = "Problem A"
    url = "https://example.com"
    add_args = SimpleNamespace(name=problem, rating=4, url=url)
    add.handle(add_args, console)
    console.clear()

    # backdate problem so it's due
    backdate_problem(problem, 5)

    take_args = SimpleNamespace(index=1, action=None, rating=None, url=True)
    take.handle(args=take_args, console=console)

    output = console.export_text()
    assert problem not in output
    assert url in output


def test_take_print_problem_from_due_problem_without_url(console, backdate_problem):
    problem = "Problem A"
    url = "https://example.com"
    add_args = SimpleNamespace(name=problem, rating=4, url=url)
    add.handle(add_args, console)
    console.clear()

    # backdate problem so it's due
    backdate_problem(problem, 5)

    take_args = SimpleNamespace(index=1, action=None, rating=None)
    take.handle(args=take_args, console=console)
    output = console.export_text()
    assert problem in output
    assert "Open in Browser" not in output


def test_take_prints_none_with_url_flag_but_no_url(console, backdate_problem):
    problem = "Problem Without URL"
    add_args = SimpleNamespace(name=problem, rating=4)
    add.handle(add_args, console)
    console.clear()

    # backdate problem so it's due
    backdate_problem(problem, 5)

    take_args = SimpleNamespace(index=1, action=None, rating=None, url=True)
    take.handle(args=take_args, console=console)
    output = console.export_text()
    assert "None" in output


# TODO: implement URL display from nextup problems in take.py
# Currently, take command URL display only works with due problems.
# The non-URL workflow can pull from nextup, but URL workflow cannot.
#
# How it works:
# - take.py always calls list_.get_due_problems(None, url_requested) at line 40
# - get_due_problems() pulls from PROGRESS_FILE and checks if problems are due (lines 67-92)
# - If no due problems exist, it falls back to nextup at lines 94-97
# - The nextup fallback returns plain names (next_up.keys()) without URL formatting
# - This is why URL display doesn't work for nextup problems
#
# Fix needed: Update get_due_problems() fallback (lines 94-97) to format URLs from nextup
# when include_url=True, similar to how it formats due problems at lines 87-92.
# def test_take_print_url(console):
#     problem1 = "Problem 1"
#     problem2 = "Problem 2"
#     url = "https://example.com"
#     nextup.handle(
#         SimpleNamespace(action="add", name=problem1),
#         console=console
#     )
#     nextup.handle(
#         SimpleNamespace(action="add", name=problem2, url=url),
#         console=console
#     )
#
#     args = SimpleNamespace(index=2, action=None, rating=None, url=True)
#     take.handle(args=args, console=console)
#     output = console.export_text()
#     assert problem2 not in output
#     assert url in output