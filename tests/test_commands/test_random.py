def test_random_command(parser):
    args = parser.parse_args(["random"])
    assert args.command == "random"
    # handler is set by the command for execution; parser should include it
    assert hasattr(args, "handler")
