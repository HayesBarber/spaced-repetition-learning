import argparse
from srl.commands import (
    add,
    list_,
    mastered,
    inprogress,
    calendar,
    nextup,
    audit,
    remove,
    config,
    take,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="srl")
    subparsers = parser.add_subparsers(dest="command")

    add.add_subparser(subparsers)
    list_.add_subparser(subparsers)
    mastered.add_subparser(subparsers)
    inprogress.add_subparser(subparsers)
    calendar.add_subparser(subparsers)
    nextup.add_subparser(subparsers)
    audit.add_subparser(subparsers)
    remove.add_subparser(subparsers)
    config.add_subparser(subparsers)
    take.add_subparser(subparsers)

    return parser
