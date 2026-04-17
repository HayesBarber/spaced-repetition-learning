from datetime import date, datetime, timedelta

from rich.console import Console

from srl.storage import PAUSE_FILE, PROGRESS_FILE, load_json, save_json
from srl.utils import today


def get_paused_on() -> date | None:
    paused_on = load_json(PAUSE_FILE).get("paused_on")
    if not paused_on:
        return None
    return date.fromisoformat(paused_on)


def is_paused() -> bool:
    return get_paused_on() is not None


def effective_today() -> date:
    return get_paused_on() or today()


def pause_schedule() -> date | None:
    paused_on = get_paused_on()
    if paused_on:
        return None

    paused_on = today()
    save_json(PAUSE_FILE, {"paused_on": paused_on.isoformat()})
    return paused_on


def clear_pause():
    save_json(PAUSE_FILE, {})


def paused_days() -> int:
    paused_on = get_paused_on()
    if not paused_on:
        return 0
    return max((today() - paused_on).days, 0)


def resume_schedule(console: Console | None = None, auto: bool = False) -> bool:
    paused_on = get_paused_on()
    if not paused_on:
        return False

    days = paused_days()
    shift_in_progress(days)
    clear_pause()

    if console is not None:
        prefix = "Automatically resumed" if auto else "Resumed"
        if days == 0:
            console.print(f"[green]{prefix}[/green] your schedule.")
        else:
            day_label = "day" if days == 1 else "days"
            console.print(
                f"[green]{prefix}[/green] your schedule after {days} paused {day_label}."
            )

    return True


def shift_in_progress(days: int) -> int:
    if days <= 0:
        return 0

    data = load_json(PROGRESS_FILE)
    shifted = 0

    for info in data.values():
        history = info.get("history", [])
        if not history:
            continue

        history[-1]["date"] = shift_iso_date(history[-1]["date"], days)
        shifted += 1

    if shifted:
        save_json(PROGRESS_FILE, data)

    return shifted


def shift_iso_date(value: str, days: int) -> str:
    if "T" in value:
        return (datetime.fromisoformat(value) + timedelta(days=days)).isoformat()

    return (date.fromisoformat(value) + timedelta(days=days)).isoformat()
