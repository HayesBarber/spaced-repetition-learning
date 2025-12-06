from srl.commands import config
from types import SimpleNamespace


def test_set_valid_audit_probability(mock_data, console, load_json):
    args = SimpleNamespace(audit_probability=0.75, get=False)
    config.handle(args, console)

    data = load_json(mock_data.CONFIG_FILE)
    assert data["audit_probability"] == 0.75

    output = console.export_text()
    assert "Audit probability set to" in output
    assert "0.75" in output


def test_set_invalid_negative_probability(mock_data, console, load_json):
    args = SimpleNamespace(audit_probability=-0.5, get=False)
    config.handle(args, console)

    data = load_json(mock_data.CONFIG_FILE)
    assert "audit_probability" not in data or data["audit_probability"] != -0.5

    output = console.export_text()
    assert "Invalid configuration option" in output


def test_set_none_probability(mock_data, console, load_json):
    args = SimpleNamespace(audit_probability=None, get=False)
    config.handle(args, console)

    data = load_json(mock_data.CONFIG_FILE)
    assert "audit_probability" not in data

    output = console.export_text()
    assert "Invalid configuration option" in output


def test_config_get(console):
    args = SimpleNamespace(audit_probability=None, get=True)
    config.handle(args, console)
    output = console.export_text()
    # Should contain a JSON object, e.g. starts with '{' or contains "audit_probability"
    assert "{" in output or "audit_probability" in output


def test_reset_colors(mock_data, console, load_json):
    args_set = SimpleNamespace(
        audit_probability=None,
        get=False,
        set_color=["1=#ffffff"],
        reset_colors=False,
    )
    config.handle(args_set, console)
    data = load_json(mock_data.CONFIG_FILE)

    # using str keys rather than ints because that is how the json is stored
    assert data["calendar_colors"] == {
        "0": "#1a1a1a",
        "1": "#ffffff",
        "2": "#33cc33",
        "3": "#00ff00",
    }

    args_reset = SimpleNamespace(
        audit_probability=None,
        get=False,
        set_color=None,
        reset_colors=True,
    )
    config.handle(args_reset, console)

    data = load_json(mock_data.CONFIG_FILE)

    assert data["calendar_colors"] == {
        "0": "#1a1a1a",
        "1": "#99e699",
        "2": "#33cc33",
        "3": "#00ff00",
    }

    output = console.export_text()
    assert "Colors reset" in output
