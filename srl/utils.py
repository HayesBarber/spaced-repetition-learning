from datetime import datetime


def today():
    return datetime.today().date()


def format_problem(problem: str, problem_url: str | None):
    """Returns "problem (url)" if url is present, otherwise "problem" """
    if problem_url:
        return f"{problem} ([blue]{problem_url}[/blue])"

    return problem
