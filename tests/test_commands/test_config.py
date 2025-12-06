from srl.commands import config
from types import SimpleNamespace
from srl.commands.config import Config
import json


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

    output = console.export_text().strip()
    data = json.loads(output)

    assert "audit_probability" in data
    assert isinstance(data["audit_probability"], float)
    assert data["audit_probability"] == 0.1
    assert "calendar_colors" in data
    assert isinstance(data["calendar_colors"], dict)
    parsed_keys = {int(k) for k in data["calendar_colors"].keys()}
    assert parsed_keys == {0, 1, 2, 3}


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


def test_set_color_valid(mock_data, console, load_json):
    args = SimpleNamespace(
        audit_probability=None,
        get=False,
        reset_colors=False,
        set_color=["2=#123456", "3=#abcdef"],
    )

    config.handle(args, console)

    data = load_json(mock_data.CONFIG_FILE)
    assert data["calendar_colors"]["2"] == "#123456"
    assert data["calendar_colors"]["3"] == "#abcdef"

    out = console.export_text()
    assert "Updated colors for level(s): 2, 3" in out


def test_set_color_invalid_format(mock_data, console, load_json):
    args = SimpleNamespace(
        audit_probability=None,
        get=False,
        reset_colors=False,
        set_color=["not-a-valid-entry"],
    )

    config.handle(args, console)

    data = load_json(mock_data.CONFIG_FILE)

    assert data["calendar_colors"] == {
        "0": "#1a1a1a",
        "1": "#99e699",
        "2": "#33cc33",
        "3": "#00ff00",
    }

    out = console.export_text()
    assert "Invalid format" in out
    assert "No valid color updates" in out


def test_config_load_converts_color_keys_to_ints(mock_data, dump_json):
    raw = {
        "audit_probability": 0.42,
        "calendar_colors": {
            "0": "#111111",
            "1": "#222222",
        },
    }
    dump_json(mock_data.CONFIG_FILE, raw)

    cfg = Config.load()

    # Keys should now be ints
    assert cfg.calendar_colors == {
        0: "#111111",
        1: "#222222",
    }
    assert cfg.audit_probability == 0.42
