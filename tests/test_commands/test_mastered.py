from srl.commands import mastered, add
from types import SimpleNamespace


def test_mastered_count(mock_data, console):
    problem = "Counting Test"
    rating = 5
    args = SimpleNamespace(name=problem, rating=rating)
    # call twice should move to mastered
    add.handle(args, console)
    add.handle(args, console)

    args = SimpleNamespace(c=True)
    mastered.handle(args=args, console=console)

    output = console.export_text()
    assert "Mastered Count:" in output
    assert "1" in output


def test_mastered_list_with_items(mock_data, console):
    problem_a = "Problem A"
    problem_b = "Problem B"

    # Add Problem A twice so it moves to mastered
    args = SimpleNamespace(name=problem_a, rating=5)
    add.handle(args, console)
    add.handle(args, console)

    # Add Problem B twice as well
    args = SimpleNamespace(name=problem_b, rating=5)
    add.handle(args, console)
    add.handle(args, console)

    args = SimpleNamespace(c=False)
    mastered.handle(args=args, console=console)

    output = console.export_text()
    assert "Mastered Problems" in output
    assert "Problem A" in output
    assert "Problem B" in output
    assert "2" in output
    assert "2" in output


def test_mastered_list_empty(mock_data, console):
    args = SimpleNamespace(c=False)
    mastered.handle(args=args, console=console)

    output = console.export_text()
    assert "No mastered problems yet" in output


def test_get_mastered_problems_filters_empty_history(mock_data, console):
    problem_a = "Problem A"

    # Add Problem A twice so it moves to mastered
    args = SimpleNamespace(name=problem_a, rating=5)
    add.handle(args, console)
    add.handle(args, console)

    result = mastered.get_mastered_problems()
    assert len(result) == 1
    assert (problem_a, 2) in result
