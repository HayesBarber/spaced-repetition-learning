from datetime import datetime


def today():
    return datetime.today().date()


def format_problem(problem: str, problem_url: str | None):
    """Returns "problem (url)" if url is present, otherwise "problem" """
    if problem_url:
        return f"{problem} ([blue]{problem_url}[/blue])"

    return problem


def _score(query: str, candidate: str) -> int | None:
    qi = 0
    score = 0
    consecutive = 0

    for i, c in enumerate(candidate):
        if qi < len(query) and c == query[qi]:
            qi += 1

            consecutive += 1
            score += 10 + consecutive * 5

            if i == 0 or candidate[i - 1] in "-_ ":
                score += 15
        else:
            consecutive = 0

    if qi != len(query):
        return None

    score -= len(candidate)
    return score


def fuzzy_find(query: str, problems: list[dict]) -> list[tuple[int, dict]]:
    matches: list[tuple[int, dict]] = []
    target = query.lower()

    for d in problems:
        problem = d.get("problem")
        if not problem:
            continue

        score = _score(target, problem.lower())
        if score is not None:
            matches.append((score, d))

    matches.sort(key=lambda x: (-x[0], x[1]["problem"]))
    return matches
