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


def fuzzy_find(query, data, extractor):
    matches = []
    target = query.lower()

    for item in data:
        problem_name = extractor(item)
        if not problem_name:
            continue

        score = _score(target, problem_name.lower())
        if score is not None:
            matches.append((score, item))

    matches.sort(key=lambda x: (-x[0], extractor(x[1])))
    return [item for score, item in matches]
