def test_random_all_command(parser):
    # random_all was folded into `random --all` — ensure parser accepts the new form
    args = parser.parse_args(["random", "--all"])
    assert args.command == "random"
    assert hasattr(args, "handler")
    assert args.all is True
