import argparse
from problems import add_or_update_problem, get_due_problems, get_mastered_problems, get_in_progress

def main():
    parser = argparse.ArgumentParser(prog="srl")
    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser("add", help="Add or update a problem attempt")
    add.add_argument("name", type=str, help="Name of the LeetCode problem")
    add.add_argument("rating", type=int, choices=range(1, 6), help="Rating from 1-5")

    list_ = subparsers.add_parser("list", help="List due problems")
    list_.add_argument("-n", type=int, default=None, help="Max number of problems")

    subparsers.add_parser("mastered", help="List mastered problems")
    
    subparsers.add_parser("inprogress", help="List problems in progress")

    args = parser.parse_args()

    if args.command == "add":
        add_or_update_problem(args.name, args.rating)
        print(f"Added rating {args.rating} for '{args.name}'")
    elif args.command == "list":
        problems = get_due_problems(args.n)
        if problems:
            print("Problems to practice today:")
            for p in problems:
                print(f" - {p}")
        else:
            print("No problems due today.")
    elif args.command == "mastered":
        mastered = get_mastered_problems()
        print("Mastered problems:")
        for m in mastered:
            print(f" - {m}")
    elif args.command == "inprogress":
        in_progress = get_in_progress()
        print("Problems in progress:")
        for p in in_progress:
            print(f" - {m}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()