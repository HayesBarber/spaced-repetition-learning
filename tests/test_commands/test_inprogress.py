from srl.commands import inprogress, add
from types import SimpleNamespace


def test_inprogress_with_items(mock_data, console, load_json):
    problem_a = "Problem A"
    problem_b = "Problem B"

    args = SimpleNamespace(name=problem_a, rating=5)
    add.handle(args, console)

    args = SimpleNamespace(name=problem_b, rating=4)
    add.handle(args, console)

    args = SimpleNamespace()
    inprogress.handle(args, console)

    data = load_json(mock_data.PROGRESS_FILE)

    output = console.export_text()
    assert "Problems in Progress (2)" in output
    assert f"1. {problem_a}" in output
    assert problem_a in data
    assert f"2. {problem_b}" in output
    assert problem_b in data


def test_inprogress_empty(console):
    args = SimpleNamespace()
    inprogress.handle(args=args, console=console)

    output = console.export_text()
    assert "No problems currently in progress" in output


def test_inprogress_empty_with_url_flag(console):
    args = SimpleNamespace(url=True)
    inprogress.handle(args=args, console=console)

    output = console.export_text()
    assert "No problems currently in progress" in output


def test_inprogress_with_items_and_urls_and_url_flag(mock_data, console, load_json):
    problem_a = "Problem A"
    url_a = "https://example.com"
    problem_b = "Problem B"
    url_b = "https://example.com"

    args = SimpleNamespace(name=problem_a, rating=5, url=url_a)
    add.handle(args, console)

    args = SimpleNamespace(name=problem_b, rating=4, url=url_b)
    add.handle(args, console)

    args = SimpleNamespace(url=True)
    inprogress.handle(args, console)

    data = load_json(mock_data.PROGRESS_FILE)

    output = console.export_text()
    assert "Problems in Progress (2)" in output
    assert f"1. {problem_a}  Open in Browser" in output
    assert problem_a in data and url_a == data[problem_a]["url"]
    assert f"2. {problem_b}  Open in Browser" in output
    assert problem_b in data and url_b == data[problem_b]["url"]

def test_inprogress_with_items_and_urls_and_no_flag(mock_data, console, load_json):
    problem_a = "Problem A"
    url_a = "https://example.com"
    problem_b = "Problem B"
    url_b = "https://example.com"

    args = SimpleNamespace(name=problem_a, rating=5, url=url_a)
    add.handle(args, console)

    args = SimpleNamespace(name=problem_b, rating=4, url=url_b)
    add.handle(args, console)

    args = SimpleNamespace()
    inprogress.handle(args, console)

    data = load_json(mock_data.PROGRESS_FILE)

    output = console.export_text()
    assert "Problems in Progress (2)" in output
    assert f"1. {problem_a}" in output
    assert problem_a in data and url_a == data[problem_a]["url"]
    assert f"2. {problem_b}" in output
    assert problem_b in data and url_b == data[problem_b]["url"]
    assert "Open in Browser" not in output

def test_inprogress_with_items_no_urls_and_url_flag(mock_data, console, load_json):
    problem_a = "Problem A"
    problem_b = "Problem B"

    args = SimpleNamespace(name=problem_a, rating=5)
    add.handle(args, console)

    args = SimpleNamespace(name=problem_b, rating=4)
    add.handle(args, console)

    args = SimpleNamespace(url=True)
    inprogress.handle(args, console)

    data = load_json(mock_data.PROGRESS_FILE)

    output = console.export_text()
    assert "Problems in Progress (2)" in output
    assert f"1. {problem_a}" in output
    assert problem_a in data
    assert f"2. {problem_b}" in output
    assert problem_b in data
    assert "Open in Browser" not in output


def test_inprogress_mixed_some_with_urls_some_without(mock_data, console, load_json):
    problem_a = "Problem A"
    url_a = "https://example.com"
    problem_b = "Problem B"

    args = SimpleNamespace(name=problem_a, rating=5, url=url_a)
    add.handle(args, console)

    args = SimpleNamespace(name=problem_b, rating=4)
    add.handle(args, console)

    args = SimpleNamespace(url=True)
    inprogress.handle(args, console)

    data = load_json(mock_data.PROGRESS_FILE)

    output = console.export_text()
    assert "Problems in Progress (2)" in output
    assert f"1. {problem_a}  Open in Browser" in output
    assert problem_a in data and url_a == data[problem_a]["url"]
    assert f"2. {problem_b}" in output
    assert problem_b in data
