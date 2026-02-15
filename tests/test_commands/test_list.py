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

    args = SimpleNamespace()
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

    args = SimpleNamespace(url=True)
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


def test_list_with_nextup_fallback_with_url_flag(console, monkeypatch):
    monkeypatch.setattr(list_, "should_audit", lambda: False)

    problem = "Next Up Problem"
    url = "https://example.com"
    args = SimpleNamespace(action="add", name=problem, url=url)
    nextup.handle(args=args, console=console)

    args = SimpleNamespace(n=None, url=True)
    list_.handle(args=args, console=console)

    output = console.export_text()
    assert problem in output
    assert "Open in Browser" in output
    assert "Problems to Practice" in output
    assert "No problems due" not in output


def test_should_audit_max_days_threshold_breached(monkeypatch, mock_data, dump_json):
    """Test that should_audit returns True when max days threshold is breached."""
    from datetime import date, timedelta

    # Set max_days_without_audit to 5
    dump_json(
        mock_data.CONFIG_FILE,
        {
            "audit_probability": 0.0,  # Zero probability, but max days should force it
            "max_days_without_audit": 5,
        },
    )

    # Set last audit date to 7 days ago (beyond threshold)
    old_date = (date.today() - timedelta(days=7)).isoformat()
    dump_json(
        mock_data.AUDIT_FILE,
        {"history": [{"date": old_date, "problem": "test", "result": "pass"}]},
    )

    assert list_.should_audit() is True


def test_should_audit_max_days_threshold_not_breached(
    monkeypatch, mock_data, dump_json
):
    """Test that should_audit falls back to probability when max days threshold not breached."""
    from datetime import date, timedelta

    # Set max_days_without_audit to 5
    dump_json(
        mock_data.CONFIG_FILE,
        {
            "audit_probability": 0.0,  # Zero probability
            "max_days_without_audit": 5,
        },
    )

    # Set last audit date to 3 days ago (within threshold)
    recent_date = (date.today() - timedelta(days=3)).isoformat()
    dump_json(
        mock_data.AUDIT_FILE,
        {"history": [{"date": recent_date, "problem": "test", "result": "pass"}]},
    )

    # With probability 0.0, should not audit
    assert list_.should_audit() is False


def test_should_audit_max_days_disabled(monkeypatch, mock_data, dump_json):
    """Test that should_audit uses probability when max days is disabled (0)."""
    from datetime import date, timedelta

    # Set max_days_without_audit to 0 (disabled)
    dump_json(
        mock_data.CONFIG_FILE,
        {
            "audit_probability": 1.0,  # 100% probability
            "max_days_without_audit": 0,
        },
    )

    # Set last audit date to 100 days ago (would trigger if enabled)
    old_date = (date.today() - timedelta(days=100)).isoformat()
    dump_json(
        mock_data.AUDIT_FILE,
        {"history": [{"date": old_date, "problem": "test", "result": "pass"}]},
    )

    # Should use probability (100%) since max days is disabled
    assert list_.should_audit() is True


def test_should_audit_no_history(monkeypatch, mock_data, dump_json):
    """Test that should_audit falls back to probability when no audit history exists."""
    dump_json(
        mock_data.CONFIG_FILE,
        {
            "audit_probability": 1.0,  # 100% probability
            "max_days_without_audit": 5,
        },
    )

    # No history in audit file
    dump_json(mock_data.AUDIT_FILE, {"history": []})

    # Should fall back to probability (100%)
    assert list_.should_audit() is True


def test_should_audit_max_days_with_no_audit_file(monkeypatch, mock_data, dump_json):
    """Test that should_audit falls back to probability when no audit file exists."""
    dump_json(
        mock_data.CONFIG_FILE,
        {
            "audit_probability": 0.0,  # 0% probability
            "max_days_without_audit": 5,
        },
    )

    # Remove audit file
    mock_data.AUDIT_FILE.unlink(missing_ok=True)

    # Should fall back to probability (0%)
    assert list_.should_audit() is False


def test_should_audit_probability_fallback_when_recent_audit(
    monkeypatch, mock_data, dump_json
):
    """Test that probability-based audit works when recent audit exists."""
    from datetime import date

    # Set max_days_without_audit to 7
    dump_json(
        mock_data.CONFIG_FILE,
        {
            "audit_probability": 1.0,  # 100% probability
            "max_days_without_audit": 7,
        },
    )

    # Set last audit date to today (very recent)
    today_date = date.today().isoformat()
    dump_json(
        mock_data.AUDIT_FILE,
        {"history": [{"date": today_date, "problem": "test", "result": "pass"}]},
    )

    # Should use probability (100%) since max days not breached
    assert list_.should_audit() is True
