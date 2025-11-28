from datetime import datetime


def today():
    return datetime.today().date()


def get_difficulty_tag(difficulty: str) -> str:
    if not difficulty:
        return ""
    color = {
        "easy": "green",
        "medium": "yellow",
        "hard": "red",
    }.get(difficulty.lower(), "white")
    return f" [{color}][{difficulty.capitalize()}][/{color}]"
