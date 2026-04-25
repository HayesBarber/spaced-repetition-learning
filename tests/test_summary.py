from datetime import date, timedelta


def test_summary_handler(parser, console, mock_data, dump_json):
    from srl.commands.summary import (
        handle,
    )

    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()

    progress_data = {
        "Problem 1": {
            "url": "http://example.com/1",
            "history": [{"date": today_str, "rating": 3}],
        },
        "Problem 2": {
            "url": "http://example.com/2",
            "history": [
                {"date": today_str, "rating": 4},
                {"date": yesterday_str, "rating": 5},
            ],
        },
    }
    mastered_data = {
        "Problem 3": {
            "url": "http://example.com/3",
            "history": [{"date": today_str, "rating": 5}],
        },
    }
    audit_data = {
        "history": [
            {"date": today_str, "problem": "Problem 3", "result": "pass"},
            {"date": yesterday_str, "problem": "Problem 3", "result": "fail"},
        ]
    }

    dump_json(mock_data.PROGRESS_FILE, progress_data)
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    dump_json(mock_data.AUDIT_FILE, audit_data)

    args = parser.parse_args(["summary"])
    handle(args, console)

    output = console.export_text()
    assert "Total Attempts:" in output
    assert "Total Mastered:" in output
    assert "Total In-Progress:" in output
    assert "Audit Stats:" in output


def test_summary_with_from_date(parser, console, mock_data, dump_json):
    from srl.commands.summary import handle

    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()
    last_week_str = (date.today() - timedelta(days=7)).isoformat()

    progress_data = {
        "Problem 1": {
            "url": "http://example.com/1",
            "history": [
                {"date": today_str, "rating": 3},
                {"date": last_week_str, "rating": 5},
            ],
        },
        "Problem 2": {
            "url": "http://example.com/2",
            "history": [{"date": last_week_str, "rating": 4}],
        },
    }
    mastered_data = {
        "Problem 3": {
            "url": "http://example.com/3",
            "history": [{"date": today_str, "rating": 5}],
        },
        "Problem 4": {
            "url": "http://example.com/4",
            "history": [
                {"date": last_week_str, "rating": 5},
            ],
        },
    }
    audit_data = {
        "history": [
            {"date": today_str, "problem": "Problem 3", "result": "pass"},
            {"date": last_week_str, "problem": "Problem 3", "result": "pass"},
        ]
    }

    dump_json(mock_data.PROGRESS_FILE, progress_data)
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    dump_json(mock_data.AUDIT_FILE, audit_data)

    from_date = (date.today() - timedelta(days=2)).isoformat()
    args = parser.parse_args(["summary", "--from-date", from_date])
    handle(args, console)

    output = console.export_text()
    assert f"Summary (since {from_date})" in output
    assert "Total Attempts: 3" in output
    assert "Total Mastered: 1" in output
    assert "Total In-Progress: 1" in output
    assert "Audit Stats:" in output
    assert "Total: 1" in output


def test_get_total_attempts_with_data(dump_json, mock_data):
    from srl.commands.summary import get_total_attempts

    today_str = date.today().isoformat()

    progress_data = {
        "Problem 1": {
            "url": "http://example.com/1",
            "history": [{"date": today_str, "rating": 3}],
        },
        "Problem 2": {
            "url": "http://example.com/2",
            "history": [
                {"date": today_str, "rating": 4},
                {"date": today_str, "rating": 5},
            ],
        },
    }
    mastered_data = {
        "Problem 3": {
            "url": "http://example.com/3",
            "history": [{"date": today_str, "rating": 5}],
        },
    }
    audit_data = {
        "history": [
            {"date": today_str, "problem": "Problem 3", "result": "pass"},
            {"date": today_str, "problem": "Problem 3", "result": "fail"},
        ]
    }

    dump_json(mock_data.PROGRESS_FILE, progress_data)
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    dump_json(mock_data.AUDIT_FILE, audit_data)

    assert get_total_attempts() == 5


def test_summary_empty_data(parser, console, mock_data, dump_json):
    from srl.commands.summary import handle

    dump_json(mock_data.PROGRESS_FILE, {})
    dump_json(mock_data.MASTERED_FILE, {})
    dump_json(mock_data.AUDIT_FILE, {})

    args = parser.parse_args(["summary"])
    handle(args, console)

    output = console.export_text()
    assert "Total Attempts: 0" in output
    assert "Total Mastered: 0" in output
    assert "Total In-Progress: 0" in output
