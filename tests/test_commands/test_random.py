from types import SimpleNamespace
from srl.commands import random as random_mod
from srl.commands import add


def test_random_no_problems(console):
    args = SimpleNamespace(all=False)
    random_mod.handle(args=args, console=console)
    output = console.export_text()
    assert "No problems available to pick from." in output


def test_random_all_empty(console):
    args = SimpleNamespace(all=True)
    random_mod.handle(args=args, console=console)
    output = console.export_text()
    assert "No problems available to pick from." in output


def test_random_all_non_dict_files(mock_data, dump_json, console):
    # write non-dict JSON into storage files and ensure handler treats them as empty
    dump_json(mock_data.PROGRESS_FILE, [])
    dump_json(mock_data.MASTERED_FILE, None)
    dump_json(mock_data.NEXT_UP_FILE, "string")

    args = SimpleNamespace(all=True)
    random_mod.handle(args=args, console=console)
    output = console.export_text()
    assert "No problems available to pick from." in output


def test_random_all_dedup_and_choice(mock_data, dump_json, console, monkeypatch):
    # same name across multiple stores — should dedupe and pick one
    dump_json(mock_data.PROGRESS_FILE, {"Alpha": {}})
    dump_json(mock_data.MASTERED_FILE, {"Alpha": {}})
    dump_json(mock_data.NEXT_UP_FILE, {"Beta": {}})

    # force deterministic choice
    monkeypatch.setattr("srl.commands.random.random.choice", lambda seq: "Alpha")

    args = SimpleNamespace(all=True)
    random_mod.handle(args=args, console=console)
    output = console.export_text()
    assert "Alpha" in output


def test_random_picks_due_problem(console, monkeypatch, backdate_problem):
    # add a problem and backdate it so it's due
    problem = "Due Problem"
    args_add = SimpleNamespace(name=problem, rating=1, number=None)
    add.handle(args=args_add, console=console)
    backdate_problem(problem, 2)

    # force deterministic choice to be the only due problem
    monkeypatch.setattr("srl.commands.random.random.choice", lambda seq: seq[0])

    args = SimpleNamespace(all=False)
    # reuse console to collect output
    random_mod.handle(args=args, console=console)
    output = console.export_text()
    assert problem in output
