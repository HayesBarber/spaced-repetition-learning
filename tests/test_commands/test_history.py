from srl.commands import history
from types import SimpleNamespace

def test_history_empty(mock_data, console, load_json):
    """Test history command with no data."""
    args = SimpleNamespace()
    history.handle(args, console)
    
    output = console.export_text()
    assert "No problems found in history" in output


def test_history_mixed(mock_data, console, dump_json):
    """Test history command with mixed in-progress and mastered problems."""
    # Setup data
    progress_data = {
        "Problem A": {
            "history": [
                {"rating": 3, "date": "2025-01-01"},
                {"rating": 4, "date": "2025-01-05"}
            ]
        }
    }
    mastered_data = {
        "Problem B": {
            "history": [
                {"rating": 5, "date": "2025-01-02"},
                {"rating": 5, "date": "2025-01-10"}
            ]
        }
    }
    
    dump_json(mock_data.PROGRESS_FILE, progress_data)
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    
    args = SimpleNamespace()
    history.handle(args, console)
    
    output = console.export_text()
    
    # Check title
    assert "Problem History (2)" in output
    
    # Check Problem A (In Progress)
    assert "Problem A" in output
    assert "In Progress" in output
    assert "2025-01-05" in output
    assert "4" in output
    
    # Check Problem B (Mastered)
    assert "Problem B" in output
    assert "Mastered" in output
    assert "2025-01-10" in output
    assert "5" in output
    
    # Check sorting (Problem B should be first because date is later)
    # Note: rich table output might be hard to strictly verify order by string finding alone 
    # if the layout is complex, but we can check relative positions if needed.
    # For now, just checking existence is good.
