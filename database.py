import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "price_flooring.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            phone_number  TEXT PRIMARY KEY,
            first_name    TEXT,
            last_name     TEXT,
            email         TEXT,
            address       TEXT,
            notes         TEXT,
            created_at    TEXT DEFAULT (datetime('now')),
            updated_at    TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS leads (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number        TEXT NOT NULL,
            customer_name       TEXT NOT NULL,
            email               TEXT,
            property_address    TEXT,
            project_type        TEXT,
            flooring_interest   TEXT,
            rooms_involved      TEXT,
            approximate_sqft    INTEGER,
            residential_or_commercial TEXT DEFAULT 'residential',
            material_only_or_install  TEXT DEFAULT 'installation',
            timeline            TEXT,
            budget_range        TEXT,
            preferred_callback  TEXT,
            notes               TEXT,
            status              TEXT DEFAULT 'new',
            created_at          TEXT DEFAULT (datetime('now')),
            updated_at          TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id          INTEGER REFERENCES leads(id),
            scheduled_date   TEXT,
            scheduled_time   TEXT,
            appointment_type TEXT DEFAULT 'estimate',
            status           TEXT DEFAULT 'scheduled',
            confirmation_num TEXT,
            assigned_to      TEXT,
            notes            TEXT,
            created_at       TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS appointment_slots (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_date    TEXT NOT NULL,
            slot_time    TEXT NOT NULL,
            is_available INTEGER DEFAULT 1,
            assigned_to  TEXT,
            slot_type    TEXT DEFAULT 'estimate'
        );
    """)
    conn.commit()
    conn.close()
