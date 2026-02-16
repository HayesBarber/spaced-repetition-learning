from srl.commands import calendar
import pytest
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


def test_get_earliest_date_empty():
    assert calendar.get_earliest_date([]) is None


def test_get_earliest_date_single():
    assert calendar.get_earliest_date(["2024-01-15"]) == date(2024, 1, 15)


def test_get_earliest_date_multiple_unsorted():
    dates = ["2024-05-01", "2023-12-01", "2024-01-01"]
    assert calendar.get_earliest_date(dates) == date(2023, 12, 1)


def test_get_earliest_date_same_values():
    dates = ["2024-01-01", "2024-01-01"]
    assert calendar.get_earliest_date(dates) == date(2024, 1, 1)


def test_calculate_months_same_month(monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2025, 2, 15)

    monkeypatch.setattr(calendar, "date", FixedDate)

    earliest = date(2025, 2, 1)
    assert calendar.calculate_months_from(earliest) == 1


def test_calculate_months_multiple(monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2025, 6, 1)

    monkeypatch.setattr(calendar, "date", FixedDate)

    earliest = date(2025, 3, 1)
    assert calendar.calculate_months_from(earliest) == 4


def test_calculate_months_cross_year(monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2025, 1, 1)

    monkeypatch.setattr(calendar, "date", FixedDate)

    earliest = date(2023, 12, 1)
    assert calendar.calculate_months_from(earliest) == 14


def test_calculate_months_future_clamped(monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2025, 1, 1)

    monkeypatch.setattr(calendar, "date", FixedDate)

    earliest = date(2025, 5, 1)
    assert calendar.calculate_months_from(earliest) == 1
