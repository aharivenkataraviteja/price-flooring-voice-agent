import sqlite3
from database import get_conn
from typing import Optional


def get_customer_by_phone(phone_number: str) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM customers WHERE phone_number = ?", (phone_number,)
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def upsert_customer(phone_number: str, first_name: str = None, last_name: str = None,
                    email: str = None, address: str = None, notes: str = None) -> dict:
    conn = get_conn()
    existing = conn.execute(
        "SELECT * FROM customers WHERE phone_number = ?", (phone_number,)
    ).fetchone()

    if existing:
        conn.execute("""
            UPDATE customers SET
                first_name = COALESCE(?, first_name),
                last_name  = COALESCE(?, last_name),
                email      = COALESCE(?, email),
                address    = COALESCE(?, address),
                notes      = COALESCE(?, notes),
                updated_at = datetime('now')
            WHERE phone_number = ?
        """, (first_name, last_name, email, address, notes, phone_number))
        action = "updated"
    else:
        conn.execute("""
            INSERT INTO customers (phone_number, first_name, last_name, email, address, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (phone_number, first_name, last_name, email, address, notes))
        action = "created"

    conn.commit()
    row = conn.execute(
        "SELECT * FROM customers WHERE phone_number = ?", (phone_number,)
    ).fetchone()
    conn.close()
    return {"action": action, "customer": dict(row)}


def create_lead(phone_number: str, customer_name: str, email: str = None,
                property_address: str = None, project_type: str = None,
                flooring_interest: str = None) -> dict:
    conn = get_conn()
    cur = conn.execute("""
        INSERT INTO leads (phone_number, customer_name, email, property_address,
                           project_type, flooring_interest)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (phone_number, customer_name, email, property_address, project_type, flooring_interest))
    lead_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"lead_id": lead_id, "status": "new"}


def update_lead_details(lead_id: int, rooms_involved: str = None, approximate_sqft: int = None,
                        residential_or_commercial: str = None, material_only_or_install: str = None,
                        timeline: str = None, budget_range: str = None,
                        preferred_callback: str = None, notes: str = None) -> dict:
    conn = get_conn()
    conn.execute("""
        UPDATE leads SET
            rooms_involved           = COALESCE(?, rooms_involved),
            approximate_sqft         = COALESCE(?, approximate_sqft),
            residential_or_commercial = COALESCE(?, residential_or_commercial),
            material_only_or_install = COALESCE(?, material_only_or_install),
            timeline                 = COALESCE(?, timeline),
            budget_range             = COALESCE(?, budget_range),
            preferred_callback       = COALESCE(?, preferred_callback),
            notes                    = COALESCE(?, notes),
            updated_at               = datetime('now')
        WHERE id = ?
    """, (rooms_involved, approximate_sqft, residential_or_commercial, material_only_or_install,
          timeline, budget_range, preferred_callback, notes, lead_id))
    conn.commit()
    row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    conn.close()
    return {"updated": True, "lead": dict(row)}


def get_available_slots(preferred_date: str = None, appointment_type: str = "estimate") -> list:
    conn = get_conn()
    if preferred_date:
        rows = conn.execute("""
            SELECT * FROM appointment_slots
            WHERE is_available = 1
              AND slot_type = ?
              AND slot_date >= ?
            ORDER BY slot_date, slot_time
            LIMIT 5
        """, (appointment_type, preferred_date)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM appointment_slots
            WHERE is_available = 1
              AND slot_type = ?
            ORDER BY slot_date, slot_time
            LIMIT 5
        """, (appointment_type,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def confirm_appointment(lead_id: int, slot_id: int = None, customer_name: str = "",
                        phone_number: str = "", appointment_type: str = "estimate",
                        preferred_date: str = None, preferred_time: str = None,
                        notes: str = None) -> dict:
    conn = get_conn()
    import random, string
    conf_num = "PF-" + "".join(random.choices(string.digits, k=6))

    if slot_id:
        slot = conn.execute(
            "SELECT * FROM appointment_slots WHERE id = ?", (slot_id,)
        ).fetchone()
        if not slot:
            conn.close()
            return {"error": "Slot not found"}
        sched_date = slot["slot_date"]
        sched_time = slot["slot_time"]
        assigned_to = slot["assigned_to"] or "our estimator"
        conn.execute(
            "UPDATE appointment_slots SET is_available = 0 WHERE id = ?", (slot_id,)
        )
    else:
        sched_date = preferred_date or "TBD — staff will confirm"
        sched_time = preferred_time or "TBD — staff will confirm"
        assigned_to = "our estimator"

    conn.execute("""
        INSERT INTO appointments
            (lead_id, scheduled_date, scheduled_time, appointment_type,
             confirmation_num, assigned_to, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (lead_id, sched_date, sched_time, appointment_type, conf_num, assigned_to, notes))

    conn.execute(
        "UPDATE leads SET status = 'appointment_set', updated_at = datetime('now') WHERE id = ?",
        (lead_id,)
    )
    conn.commit()
    conn.close()
    return {
        "confirmation_number": conf_num,
        "date": sched_date,
        "time": sched_time,
        "assigned_to": assigned_to,
        "appointment_type": appointment_type
    }


def get_leads(limit: int = 50) -> list:
    conn = get_conn()
    rows = conn.execute("""
        SELECT l.*, a.scheduled_date, a.scheduled_time, a.confirmation_num
        FROM leads l
        LEFT JOIN appointments a ON a.lead_id = l.id
        ORDER BY l.created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
