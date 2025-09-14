from srl.commands import add
import json
from types import SimpleNamespace


def test_add_new_problem(tmp_path, console):
    problem = "What is 2+2?"
    rating = 3
    args = SimpleNamespace(name=problem, rating=rating)

    add.handle(
        args=args,
        console=console,
    )

    progress_file = tmp_path / "problems_in_progress.json"
    with open(progress_file) as f:
        progress = json.load(f)
    assert problem in progress
    assert progress[problem]["history"][0]["rating"] == rating

    output = console.export_text()
    assert f"Added rating {rating} for '{problem}'"
