import argparse
from problems import *
from storage import ensure_data_dir, load_json, NEXT_UP_FILE
from rich.table import Table
from rich.console import Console
from rich.panel import Panel


def main():
    ensure_data_dir()

    args = parser.parse_args()

    console = Console()

    parser.print_help()


if __name__ == "__main__":
    main()
