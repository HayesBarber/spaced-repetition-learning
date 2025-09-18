from srl.commands import config
from types import SimpleNamespace


def test_set_valid_audit_probability(mock_data, console, load_json):
    args = SimpleNamespace(audit_probability=0.75)
    config.handle(args, console)

    data = load_json(mock_data.CONFIG_FILE)
    assert data["audit_probability"] == 0.75

    output = console.export_text()
    assert "Audit probability set to" in output
    assert "0.75" in output


def test_set_invalid_negative_probability(mock_data, console, load_json):
    args = SimpleNamespace(audit_probability=-0.5)
    config.handle(args, console)

    data = load_json(mock_data.CONFIG_FILE)
    assert "audit_probability" not in data or data["audit_probability"] != -0.5

    output = console.export_text()
    assert "Invalid configuration option" in output


def test_set_none_probability(mock_data, console, load_json):
    args = SimpleNamespace(audit_probability=None)
    config.handle(args, console)

    data = load_json(mock_data.CONFIG_FILE)
    assert "audit_probability" not in data

    output = console.export_text()
    assert "Invalid configuration option" in output
