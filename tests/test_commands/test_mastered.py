from srl.commands import mastered, add
from types import SimpleNamespace


def test_mastered_count(console):
    problem = "Counting Test"
    rating = 5
    args = SimpleNamespace(number=None, name=problem, rating=rating)
    # call twice should move to mastered
    add.handle(args, console)
    add.handle(args, console)

    args = SimpleNamespace(c=True)
    mastered.handle(args=args, console=console)

    output = console.export_text()
    assert "Mastered Count:" in output
    assert "1" in output


def test_mastered_list_with_items(console, today_string):
    problem_a = "Problem A"
    problem_b = "Problem B"

    args = SimpleNamespace(number=None, name=problem_a, rating=5)
    add.handle(args, console)
    add.handle(args, console)

    args = SimpleNamespace(number=None, name=problem_b, rating=5)
    add.handle(args, console)
    args = SimpleNamespace(number=None, name=problem_b, rating=1)
    add.handle(args, console)
    args = SimpleNamespace(number=None, name=problem_b, rating=5)
    add.handle(args, console)
    add.handle(args, console)

    args = SimpleNamespace(c=False)
    mastered.handle(args=args, console=console)

    output = console.export_text()
    assert "Mastered Problems (2)" in output
    assert "Problem A" in output
    assert "2" in output
    assert "Problem B" in output
    assert "4" in output
    assert today_string in output


def test_mastered_list_empty(console):
    args = SimpleNamespace(c=False)
    mastered.handle(args=args, console=console)

    output = console.export_text()
    assert "No mastered problems yet" in output


def test_get_mastered_problems_filters_empty_history(console, today_string):
    problem_a = "Problem A"

    args = SimpleNamespace(number=None, name=problem_a, rating=5)
    add.handle(args, console)
    add.handle(args, console)

    result = mastered.get_mastered_problems()
    assert len(result) == 1
    assert (problem_a, 2, today_string) in result
