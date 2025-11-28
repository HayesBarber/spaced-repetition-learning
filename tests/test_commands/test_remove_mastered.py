from srl.commands import remove
from types import SimpleNamespace

def test_remove_mastered(mock_data, console, load_json, dump_json):
    """Test removing a problem from the mastered list."""
    problem = "Mastered Problem"
    mastered_data = {problem: {"history": []}}
    dump_json(mock_data.MASTERED_FILE, mastered_data)
    
    args = SimpleNamespace(name=problem)
    remove.handle(args, console)
    
    # Verify removed
    mastered = load_json(mock_data.MASTERED_FILE)
    assert problem not in mastered
    
    output = console.export_text()
    assert f"Removed '{problem}' from mastered." in output

def test_remove_both(mock_data, console, load_json, dump_json):
    """Test removing a problem that exists in both lists (edge case)."""
    problem = "Duplicate Problem"
    data = {problem: {"history": []}}
    dump_json(mock_data.PROGRESS_FILE, data)
    dump_json(mock_data.MASTERED_FILE, data)
    
    args = SimpleNamespace(name=problem)
    remove.handle(args, console)
    
    # Verify removed from both
    progress = load_json(mock_data.PROGRESS_FILE)
    mastered = load_json(mock_data.MASTERED_FILE)
    assert problem not in progress
    assert problem not in mastered
    
    output = console.export_text()
    assert f"Removed '{problem}' from in-progress and mastered." in output

def test_remove_not_found(mock_data, console):
    """Test removing a non-existent problem."""
    problem = "Ghost Problem"
    args = SimpleNamespace(name=problem)
    remove.handle(args, console)
    
    output = console.export_text()
    assert f"Problem '{problem}' not found." in output
