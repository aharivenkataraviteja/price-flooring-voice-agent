"""
Run this script to pre-populate appointment slots for the next 2 weeks.
Edit the configuration below to match the team's actual schedule.
Re-run weekly to keep slots fresh.

Usage:
  python3 seed_slots.py
"""
import sqlite3
from datetime import date, timedelta
import os

DB_PATH = os.getenv("DB_PATH", "price_flooring.db")

# Estimator names (rotate or assign as needed)
ESTIMATORS = ["Ray", "Peter", "Lucien"]

# Slots to offer per available weekday
WEEKDAY_SLOTS = [
    ("09:00 AM", "estimate"),
    ("11:00 AM", "estimate"),
    ("02:00 PM", "estimate"),
    ("04:00 PM", "estimate"),
]

# Saturday slots (showroom open, lighter schedule)
SATURDAY_SLOTS = [
    ("10:00 AM", "consultation"),
    ("01:00 PM", "consultation"),
]

def seed():
    conn = sqlite3.connect(DB_PATH)
    today = date.today()
    inserted = 0

    for i in range(14):  # next 14 days
        d = today + timedelta(days=i)
        dow = d.weekday()  # 0=Mon, 6=Sun

        if dow == 6:  # Sunday — skip
            continue

        slots = SATURDAY_SLOTS if dow == 5 else WEEKDAY_SLOTS

        for j, (slot_time, slot_type) in enumerate(slots):
            assigned = ESTIMATORS[j % len(ESTIMATORS)]
            existing = conn.execute(
                "SELECT id FROM appointment_slots WHERE slot_date = ? AND slot_time = ? AND slot_type = ?",
                (str(d), slot_time, slot_type)
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO appointment_slots (slot_date, slot_time, is_available, assigned_to, slot_type) VALUES (?,?,1,?,?)",
                    (str(d), slot_time, assigned, slot_type)
                )
                inserted += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted} new slots.")

if __name__ == "__main__":
    seed()
