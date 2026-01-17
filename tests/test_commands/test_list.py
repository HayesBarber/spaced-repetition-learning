from srl.commands import list_, add, nextup
from types import SimpleNamespace


def test_list_with_due_problem(console, monkeypatch, backdate_problem):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Due Problem"
    # Add problem with rating=1, then backdate it so it's due
    args = SimpleNamespace(name=problem, rating=1)
    add.handle(args=args, console=console)
    backdate_problem(problem, 2)

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "Problems to Practice" in output
    assert "(1)" in output
    assert problem in output


def test_list_with_limit(console, monkeypatch, backdate_problem):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    for i in range(10):
        problem = f"problem {i}"
        args = SimpleNamespace(name=problem, rating=1)
        add.handle(args=args, console=console)
        backdate_problem(problem, 2)

    console.clear()
    args = SimpleNamespace(n=3)
    list_.handle(args=args, console=console)

    output = console.export_text()
    for i in range(3):
        assert f"problem {i}" in output
    for i in range(3, 10):
        assert f"problem {i}" not in output


def test_list_with_next_up_fallback(console, monkeypatch):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Next Up Problem"
    args = SimpleNamespace(action="add", name=problem)
    nextup.handle(args=args, console=console)

    args = SimpleNamespace(n=None)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert problem in output
    assert "Problems to Practice" in output
    assert "No problems due" not in output


def test_list_empty(console, monkeypatch):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "No problems due today or in Next Up" in output


def test_should_audit_probability(monkeypatch):
    monkeypatch.setattr(list_, "load_json", lambda _: {"audit_probability": 1.0})
    monkeypatch.setattr(list_.random, "random", lambda: 0.0)  # force audit
    assert list_.should_audit() is True

    monkeypatch.setattr(list_, "load_json", lambda _: {"audit_probability": 0.0})
    monkeypatch.setattr(list_.random, "random", lambda: 1.0)  # force no audit
    assert list_.should_audit() is False


def test_list_triggers_audit(console, monkeypatch):
    problem = "Audit Problem"
    args = SimpleNamespace(name=problem, rating=5)
    add.handle(args=args, console=console)
    add.handle(args=args, console=console)  # move to mastered

    monkeypatch.setattr(list_, "should_audit", lambda: True)

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "You have been randomly audited!" in output
    assert "Audit problem:" in output
    assert problem in output


def test_list_indicate_mastered(console, backdate_problem, monkeypatch):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Mastered attempt"
    args = SimpleNamespace(name=problem, rating=5)
    add.handle(args=args, console=console)
    backdate_problem(problem, 7)

    args = SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert f"1. {problem} *" in output


def test_list_displays_url_with_flag(console, monkeypatch, backdate_problem):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Due Problem"
    url = "https://example.com/"

    # Add problem with rating=1, then backdate it so it's due
    args = SimpleNamespace(name=problem, rating=1, url=url)
    add.handle(args=args, console=console)
    backdate_problem(problem, 2)

    args = SimpleNamespace(url=True)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "Problems to Practice" in output
    assert "(1)" in output
    assert problem in output
    assert "Open in Browser" in output


def test_list_hides_url_without_flag(console, monkeypatch, backdate_problem):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Due Problem"
    url = "https://example.com"

    args = SimpleNamespace(name=problem, rating=1, url=url)
    add.handle(args=args, console=console)
    backdate_problem(problem, 2)

    args= SimpleNamespace()
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "Problems to Practice" in output
    assert "(1)" in output
    assert problem in output
    assert "Open in Browser" not in output


def test_list_missing_url_not_displayed(console, monkeypatch, backdate_problem):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Due Problem"

    args = SimpleNamespace(name=problem, rating=1)
    add.handle(args=args, console=console)
    backdate_problem(problem, 2)

    args= SimpleNamespace(url=True)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "Problems to Practice" in output
    assert "(1)" in output
    assert problem in output
    assert "Open in Browser" not in output


def test_list_with_mixed_urls(console, monkeypatch, backdate_problem):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem_with_url = "Problem With URL"
    problem_without_url = "Problem Without URL"
    url = "https://example.com"

    # Add problem with URL
    args = SimpleNamespace(name=problem_with_url, rating=1, url=url)
    add.handle(args=args, console=console)
    backdate_problem(problem_with_url, 2)

    # Add problem without URL
    args = SimpleNamespace(name=problem_without_url, rating=1)
    add.handle(args=args, console=console)
    backdate_problem(problem_without_url, 2)

    args = SimpleNamespace(url=True)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert problem_with_url in output
    assert problem_without_url in output
    assert output.count("Open in Browser") == 1


def test_list_empty_with_url_flag(console, monkeypatch):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    args = SimpleNamespace(url=True)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert "No problems due today or in Next Up" in output


# TODO: implement this functionality
# def test_list_with_nextup_fallback_with_url_flag(console, monkeypatch):
#     monkeypatch.setattr(list_, "should_audit", lambda: False)

#     problem = "Next Up Problem"
#     url = "https://example.com"
#     args = SimpleNamespace(action="add", name=problem, url=url)
#     nextup.handle(args=args, console=console)

#     args= SimpleNamespace(n=None, url=True)
#     list_.handle(args=args, console=console)

#     output = console.export_text()
#     assert problem in output
#     assert "Open in Browser" in output
#     assert "Problems to Practice" in output
#     assert "No problems due" not in output
