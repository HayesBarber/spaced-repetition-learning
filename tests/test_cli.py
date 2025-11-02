import pytest
from srl import cli


@pytest.fixture
def parser():
    return cli.build_parser()


def test_add_command(parser):
    args = parser.parse_args(["add", "Two Sum", "3"])
    assert args.command == "add"
    assert args.name == "Two Sum"
    assert args.rating == 3


def test_add_invalid_rating(parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["add", "Two Sum", "7"])


def test_list_with_n(parser):
    args = parser.parse_args(["list", "-n", "5"])
    assert args.command == "list"
    assert args.n == 5


def test_mastered_count(parser):
    args = parser.parse_args(["mastered", "-c"])
    assert args.command == "mastered"
    assert args.c is True


def test_nextup_add(parser):
    args = parser.parse_args(["nextup", "add", "Binary Search"])
    assert args.command == "nextup"
    assert args.action == "add"
    assert args.name == "Binary Search"


def test_nextup_list(parser):
    args = parser.parse_args(["nextup", "list"])
    assert args.command == "nextup"
    assert args.action == "list"
    assert args.name is None


def test_audit_pass(parser):
    args = parser.parse_args(["audit", "--pass"])
    assert args.command == "audit"
    assert args.audit_pass is True
    assert args.audit_fail is False


def test_remove(parser):
    args = parser.parse_args(["remove", "Palindrome Number"])
    assert args.command == "remove"
    assert args.name == "Palindrome Number"


def test_config_audit_probability(parser):
    args = parser.parse_args(["config", "--audit-probability", "0.3"])
    assert args.command == "config"
    assert args.audit_probability == 0.3


def test_config_get(parser):
    args = parser.parse_args(["config", "--get"])
    assert args.command == "config"
    assert args.get is True


def test_take_command_basic(parser):
    args = parser.parse_args(["take", "1"])
    assert args.command == "take"
    assert args.index == 1
    assert args.action is None
    assert args.rating is None


def test_take_command_add_with_rating(parser):
    args = parser.parse_args(["take", "2", "add", "5"])
    assert args.command == "take"
    assert args.index == 2
    assert args.action == "add"
    assert args.rating == 5


def test_take_command_invalid_index(parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["take", "-1"])


def test_take_command_invalid_action(parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["take", "0", "invalid"])


def test_take_command_add_invalid_rating(parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["take", "3", "add", "-3"])


def test_calendar_command(parser):
    args = parser.parse_args(["calendar"])
    assert args.command == "calendar"
    assert args.months == 12


def test_calendar_with_months_long(parser):
    args = parser.parse_args(["calendar", "--months", "6"])
    assert args.command == "calendar"
    assert args.months == 6


def test_calendar_with_months_short(parser):
    args = parser.parse_args(["calendar", "-m", "3"])
    assert args.command == "calendar"
    assert args.months == 3


def test_server_defaults(parser):
    args = parser.parse_args(["server"])
    assert args.command == "server"
    assert args.host == "127.0.0.1"
    assert args.port == 8080
    assert args.reload is False
    assert args.public is False


def test_server_public_flag(parser):
    args = parser.parse_args(["server", "--public"])
    assert args.command == "server"
    assert args.public is True
    # host remains the default in parsed args; server handler may translate this to 0.0.0.0
    assert args.host == "127.0.0.1"


def test_server_custom_host_port_reload(parser):
    args = parser.parse_args(
        ["server", "--host", "0.0.0.0", "--port", "9000", "--reload"]
    )
    assert args.command == "server"
    assert args.host == "0.0.0.0"
    assert args.port == 9000
    assert args.reload is True
