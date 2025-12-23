# Contributing

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/HayesBarber/spaced-repetition-learning.git
cd spaced-repetition-learning
```

2. Install the package with dev dependencies:

Install with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install -e ".[dev]"
```

## Running Tests

Run the test suite with pytest:

```bash
pytest
```

Or with uv:

```bash
uv run pytest
```

To run tests with verbose output:

```bash
pytest -v
```

To run a specific test file:

```bash
pytest tests/test_cli.py
```

## Project Structure

- `srl/` - Main package source code
- `srl/commands/` - CLI command implementations
- `tests/` - Test suite
- `starter_data/` - Sample problem lists (Blind 75, NeetCode 150, etc.)
