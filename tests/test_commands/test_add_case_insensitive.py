from srl.commands import add
from types import SimpleNamespace

def test_add_case_insensitive_update(mock_data, console, load_json):
    """
    Verify that adding a problem with different casing updates the existing entry
    instead of creating a new one.
    """
    problem_original = "Test Problem"
    problem_variant = "test problem"
    rating1 = 1
    rating2 = 2
    
    # 1. Add original problem
    args1 = SimpleNamespace(name=problem_original, rating=rating1)
    add.handle(args=args1, console=console)
    
    # Verify it exists
    progress_file = mock_data.PROGRESS_FILE
    progress = load_json(progress_file)
    assert problem_original in progress
    assert len(progress) == 1
    assert progress[problem_original]["history"][0]["rating"] == rating1

    # 2. Add variant (different casing)
    args2 = SimpleNamespace(name=problem_variant, rating=rating2)
    add.handle(args=args2, console=console)
    
    # Verify we still have only 1 entry (the original key)
    progress = load_json(progress_file)
    
    assert len(progress) == 1, f"Expected 1 entry, found {len(progress)}: {list(progress.keys())}"
    assert problem_original in progress
    assert problem_variant not in progress
    
    # Verify history was updated
    history = progress[problem_original]["history"]
    assert len(history) == 2
    assert history[1]["rating"] == rating2
