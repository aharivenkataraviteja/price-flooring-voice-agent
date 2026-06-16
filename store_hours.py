import pytz
from datetime import datetime
import os

TIMEZONE = os.getenv("TIMEZONE", "America/New_York")

HOURS = {
    0: ("08:30", "17:00"),  # Monday
    1: ("08:30", "17:00"),  # Tuesday
    2: ("08:30", "17:00"),  # Wednesday
    3: ("08:30", "17:00"),  # Thursday
    4: ("08:30", "17:00"),  # Friday
    5: ("09:00", "16:00"),  # Saturday
    6: None,                 # Sunday — closed
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_store_status() -> dict:
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    dow = now.weekday()
    today_hours = HOURS[dow]

    if today_hours is None:
        next_open = _next_open_day(dow)
        return {
            "is_open": False,
            "current_day": DAY_NAMES[dow],
            "opens_at": None,
            "closes_at": None,
            "message": f"We're closed today (Sunday). We reopen {next_open}.",
            "next_opening": next_open
        }

    open_h, open_m = map(int, today_hours[0].split(":"))
    close_h, close_m = map(int, today_hours[1].split(":"))
    open_dt = now.replace(hour=open_h, minute=open_m, second=0, microsecond=0)
    close_dt = now.replace(hour=close_h, minute=close_m, second=0, microsecond=0)

    is_open = open_dt <= now < close_dt
    opens_at_str = _fmt(today_hours[0])
    closes_at_str = _fmt(today_hours[1])

    if is_open:
        message = f"We're open today {DAY_NAMES[dow]} until {closes_at_str}."
    else:
        next_open = _next_open_day(dow) if now >= close_dt else f"today at {opens_at_str}"
        message = f"We're currently closed. {'We open ' + next_open + '.' if now >= close_dt else 'We open ' + opens_at_str + ' today.'}"
        if now >= close_dt:
            next_open = _next_open_day(dow)

    return {
        "is_open": is_open,
        "current_day": DAY_NAMES[dow],
        "opens_at": opens_at_str,
        "closes_at": closes_at_str,
        "message": message,
        "next_opening": _next_open_day(dow) if not is_open else None
    }


def _fmt(t: str) -> str:
    h, m = map(int, t.split(":"))
    suffix = "AM" if h < 12 else "PM"
    h12 = h if h <= 12 else h - 12
    if h12 == 0:
        h12 = 12
    return f"{h12}:{m:02d} {suffix}"


def _next_open_day(current_dow: int) -> str:
    for offset in range(1, 8):
        next_dow = (current_dow + offset) % 7
        if HOURS[next_dow] is not None:
            return f"{DAY_NAMES[next_dow]} at {_fmt(HOURS[next_dow][0])}"
    return "Monday at 8:30 AM"
