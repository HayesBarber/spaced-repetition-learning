from rich.console import Console
from srl.commands import add
import json
from types import SimpleNamespace


def test_add_new_problem(tmp_path, monkeypatch):
    progress_file = tmp_path / "problems_in_progress.json"
    mastered_file = tmp_path / "problems_mastered.json"
    next_up_file = tmp_path / "next_up.json"

    progress_file.write_text("{}")
    mastered_file.write_text("{}")
    next_up_file.write_text("[]")

    monkeypatch.setattr(add, "PROGRESS_FILE", progress_file)
    monkeypatch.setattr(add, "MASTERED_FILE", mastered_file)
    monkeypatch.setattr(add, "NEXT_UP_FILE", next_up_file)

    console = Console(record=True)

    problem = "What is 2+2?"
    rating = 3
    args = SimpleNamespace(name=problem, rating=rating)

    add.handle(
        args=args,
        console=console,
    )

    with open(progress_file) as f:
        progress = json.load(f)
    assert problem in progress
    assert progress[problem]["history"][0]["rating"] == rating

    output = console.export_text()
    assert f"Added rating {rating} for '{problem}'"
