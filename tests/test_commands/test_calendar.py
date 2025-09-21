from srl.commands import calendar


def test_get_audit_dates(mock_data, dump_json):
    mock_audit_data = {
        "history": [
            {"date": "2024-06-06", "problem": "problem3", "result": "pass"},
            {"date": "2024-06-07", "problem": "problem3", "result": "fail"},
            {"date": "2024-06-08", "problem": "problem3", "result": "pass"},
        ]
    }
    dump_json(mock_data.AUDIT_FILE, mock_audit_data)

    result = calendar.get_audit_dates()

    assert result == ["2024-06-06", "2024-06-08"]


def test_get_dates(mock_data, dump_json):
    mock_mastered_data = {
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
    dump_json(mock_data.MASTERED_FILE, mock_mastered_data)

    result = calendar.get_dates(mock_data.MASTERED_FILE)

    assert result == ["2024-06-01", "2024-06-02", "2024-06-01", "2024-06-03"]


def test_get_all_date_counts(mock_data, dump_json):
    mock_audit_data = {
        "history": [
            {"date": "2024-06-06", "problem": "problem3", "result": "pass"},
            {"date": "2024-06-07", "problem": "problem3", "result": "fail"},
            {"date": "2024-06-08", "problem": "problem3", "result": "pass"},
        ]
    }
    dump_json(mock_data.AUDIT_FILE, mock_audit_data)

    mock_mastered_data = {
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
    dump_json(mock_data.MASTERED_FILE, mock_mastered_data)

    mock_inprogress_data = {
        "problem3": {
            "history": [
                {"rating": 5, "date": "2024-06-04"},
                {"rating": 5, "date": "2024-06-05"},
            ]
        }
    }
    dump_json(mock_data.PROGRESS_FILE, mock_inprogress_data)

    result = calendar.get_all_date_counts()

    assert result["2024-06-01"] == 2  # Two history entries from mastered data
    assert result["2024-06-02"] == 1
    assert result["2024-06-03"] == 1
    assert result["2024-06-04"] == 1
    assert result["2024-06-05"] == 1
    assert result["2024-06-06"] == 1  # audit pass
    assert result["2024-06-08"] == 1  # audit pass
    assert "2024-06-07" not in result  # audit fail, should not be included
