def test_random_all_command(parser):
    args = parser.parse_args(["random_all"])
    assert args.command == "random_all"
    assert hasattr(args, "handler")
