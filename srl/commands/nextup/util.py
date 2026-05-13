from srl.storage import (
    load_json,
    NEXT_UP_FILE,
)


def get_next_up_problems() -> list[tuple[str, str]]:
    """
    returns a list of tuples (name, url)
    """
    data = load_json(NEXT_UP_FILE)
    res = []

    for name, info in data.items():
        res.append((name, info.get("url", "")))

    return res
