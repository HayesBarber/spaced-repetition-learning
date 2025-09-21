from srl.commands import calendar
import pytest
from collections import Counter
from datetime import date


@pytest.fixture
def audit_data_pass_fail():
    return {
        "history": [
            {"date": "2024-06-06", "problem": "problem3", "result": "pass"},
            {"date": "2024-06-07", "problem": "problem3", "result": "fail"},
            {"date": "2024-06-08", "problem": "problem3", "result": "pass"},
        ]
    }


@pytest.fixture
def mastered_data():
    return {
        "problem1": {
            "history": [
                {"rating": 3, "date": "2024-06-01"},
                {"rating": 5, "date": "2024-06-02"},
            ]
        },
        "problem2": {
            "history": [
                {"rating": 3, "date": "2024-06-01"},
                {"rating": 4, "date": "2024-06-03"},
            ]
        },
    }


@pytest.fixture
def inprogress_data():
    return {
        "problem3": {
            "history": [
                {"rating": 5, "date": "2024-06-04"},
                {"rating": 5, "date": "2024-06-05"},
            ]
        }
    }


def test_get_audit_dates(mock_data, dump_json, audit_data_pass_fail):
    dump_json(mock_data.AUDIT_FILE, audit_data_pass_fail)

    result = calendar.get_audit_dates()

    assert result == ["2024-06-06", "2024-06-08"]


def test_get_dates(mock_data, dump_json, mastered_data):
    dump_json(mock_data.MASTERED_FILE, mastered_data)

    result = calendar.get_dates(mock_data.MASTERED_FILE)

    assert result == ["2024-06-01", "2024-06-02", "2024-06-01", "2024-06-03"]


def test_get_all_date_counts(
    mock_data,
    dump_json,
    audit_data_pass_fail,
    mastered_data,
    inprogress_data,
):
    dump_json(mock_data.AUDIT_FILE, audit_data_pass_fail)
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    dump_json(mock_data.PROGRESS_FILE, inprogress_data)

    result = calendar.get_all_date_counts()

    assert result["2024-06-01"] == 2  # Two history entries from mastered data
    assert result["2024-06-02"] == 1
    assert result["2024-06-03"] == 1
    assert result["2024-06-04"] == 1
    assert result["2024-06-05"] == 1
    assert result["2024-06-06"] == 1  # audit pass
    assert result["2024-06-08"] == 1  # audit pass
    assert "2024-06-07" not in result  # audit fail, should not be included


def test_build_weeks_with_start_and_today():
    start = date(2019, 6, 3)  # Monday
    today = date(2019, 6, 8)

    counts = Counter(
        {
            "2019-06-02": 1,  # Sunday
            "2019-06-04": 3,  # Tuesday
            "2019-06-07": 2,  # Friday
        }
    )

    weeks = calendar.build_weeks(counts, start=start, today=today)

    assert len(weeks) == 1
    week = weeks[0]
    assert len(week) == 7

    assert week[0] == 1
    assert week[1] == 0
    assert week[2] == 3
    assert week[3] == 0
    assert week[4] == 0
    assert week[5] == 2
    assert week[6] == 0

    assert all(day is not None for day in week)
