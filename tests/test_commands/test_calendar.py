from srl.commands import calendar
from datetime import date
from types import SimpleNamespace
import pytest


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
def audit_data_earlier():
    return {
        "history": [
            {"date": "2024-01-15", "problem": "problem1", "result": "pass"},
            {"date": "2024-03-20", "problem": "problem2", "result": "pass"},
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
def mastered_data_earlier():
    return {
        "problem1": {
            "history": [
                {"rating": 3, "date": "2023-12-10"},
                {"rating": 5, "date": "2024-02-15"},
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


@pytest.fixture
def inprogress_data_earlier():
    return {
        "problem4": {
            "history": [
                {"rating": 5, "date": "2024-02-01"},
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


def test_get_earliest_date_from_audit(mock_data, dump_json, audit_data_earlier):
    dump_json(mock_data.AUDIT_FILE, audit_data_earlier)
    dump_json(mock_data.MASTERED_FILE, {})
    dump_json(mock_data.PROGRESS_FILE, {})

    result = calendar.get_earliest_date()

    assert result == date(2024, 1, 15)


def test_get_earliest_date_from_mastered(mock_data, dump_json, mastered_data_earlier):
    dump_json(mock_data.AUDIT_FILE, {})
    dump_json(mock_data.MASTERED_FILE, mastered_data_earlier)
    dump_json(mock_data.PROGRESS_FILE, {})

    result = calendar.get_earliest_date()

    assert result == date(2023, 12, 10)


def test_get_earliest_date_from_inprogress(
    mock_data, dump_json, inprogress_data_earlier
):
    dump_json(mock_data.AUDIT_FILE, {})
    dump_json(mock_data.MASTERED_FILE, {})
    dump_json(mock_data.PROGRESS_FILE, inprogress_data_earlier)

    result = calendar.get_earliest_date()

    assert result == date(2024, 2, 1)


def test_get_earliest_date_across_all_files(
    mock_data,
    dump_json,
    audit_data_earlier,
    mastered_data_earlier,
    inprogress_data_earlier,
):
    # 2023-12-10 in mastered, 2024-01-15 in audit, 2024-02-01 in progress
    dump_json(mock_data.AUDIT_FILE, audit_data_earlier)
    dump_json(mock_data.MASTERED_FILE, mastered_data_earlier)
    dump_json(mock_data.PROGRESS_FILE, inprogress_data_earlier)

    result = calendar.get_earliest_date()

    assert result == date(2023, 12, 10)


def test_get_earliest_date_no_data(mock_data, dump_json):
    dump_json(mock_data.AUDIT_FILE, {})
    dump_json(mock_data.MASTERED_FILE, {})
    dump_json(mock_data.PROGRESS_FILE, {})

    result = calendar.get_earliest_date()

    assert result is None


def test_calculate_months_returns_postive_integer():
    earliest = date(2024, 6, 15)
    result = calendar.calculate_months_from(earliest)
    assert result >= 1


def test_calculate_months_from_previous_year():
    earliest = date(2023, 1, 1)
    today = date.today()
    expected_months = (today.year - 2023) * 12 + (today.month - 1) + 1
    result = calendar.calculate_months_from(earliest)
    assert result == expected_months


def test_handle_from_first_flag_with_data(
    mock_data,
    dump_json,
    console,
    mastered_data_earlier,
):
    dump_json(mock_data.MASTERED_FILE, mastered_data_earlier)
    dump_json(mock_data.PROGRESS_FILE, {})
    dump_json(mock_data.AUDIT_FILE, {})

    args = SimpleNamespace(from_first=True)
    calendar.handle(args, console)

    output = console.export_text()
    assert "Less" in output or "More" in output


def test_handle_from_first_flag_no_data(mock_data, dump_json, console):
    dump_json(mock_data.MASTERED_FILE, {})
    dump_json(mock_data.PROGRESS_FILE, {})
    dump_json(mock_data.AUDIT_FILE, {})

    args = SimpleNamespace(from_first=True)
    calendar.handle(args, console)

    output = console.export_text()
    assert "No recorded dates found" in output
