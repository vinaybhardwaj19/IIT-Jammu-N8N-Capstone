"""
CRM Database — Real SQLite Persistence Layer
=============================================
Replaces in-memory dict with a real SQLite database.
Tracks leads, activities, emails, and pipeline stages.
"""

import sqlite3
import json
import os
import re
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'salesai.db')


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    # SQLite disables FK enforcement per connection unless explicitly enabled.
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_database():
    """Initialize all tables if they don't exist."""
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS leads (
            lead_id         TEXT PRIMARY KEY,
            full_name       TEXT,
            role            TEXT,
            email           TEXT,
            phone           TEXT,
            company         TEXT,
            industry        TEXT,
            website         TEXT,
            budget          TEXT,
            source          TEXT,
            notes           TEXT,
            pipeline_stage  TEXT DEFAULT 'New Lead',
            lead_temperature TEXT DEFAULT 'Cold',
            composite_score INTEGER DEFAULT 0,
            deal_probability INTEGER DEFAULT 0,
            estimated_deal_size TEXT,
            assigned_to     TEXT DEFAULT 'Unassigned',
            created_at      TEXT,
            updated_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS research_results (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id         TEXT,
            intelligence    TEXT,
            researched_at   TEXT,
            FOREIGN KEY(lead_id) REFERENCES leads(lead_id)
        );

        CREATE TABLE IF NOT EXISTS qualification_results (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id         TEXT,
            bant_scores     TEXT,
            qualification   TEXT,
            qualified_at    TEXT,
            FOREIGN KEY(lead_id) REFERENCES leads(lead_id)
        );

        CREATE TABLE IF NOT EXISTS emails (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id         TEXT,
            email_type      TEXT,
            subject_a       TEXT,
            subject_b       TEXT,
            body_html       TEXT,
            plain_text      TEXT,
            linkedin_msg    TEXT,
            cta             TEXT,
            reply_rate_est  TEXT,
            sent            INTEGER DEFAULT 0,
            sent_at         TEXT,
            opened          INTEGER DEFAULT 0,
            replied         INTEGER DEFAULT 0,
            written_at      TEXT,
            FOREIGN KEY(lead_id) REFERENCES leads(lead_id)
        );

        CREATE TABLE IF NOT EXISTS activities (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id         TEXT,
            activity_type   TEXT,
            description     TEXT,
            outcome         TEXT,
            performed_by    TEXT DEFAULT 'SalesAI',
            created_at      TEXT,
            FOREIGN KEY(lead_id) REFERENCES leads(lead_id)
        );

        CREATE TABLE IF NOT EXISTS meetings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id         TEXT,
            title           TEXT,
            scheduled_at    TEXT,
            duration_minutes INTEGER DEFAULT 30,
            meeting_link    TEXT,
            status          TEXT DEFAULT 'Scheduled',
            notes           TEXT,
            created_at      TEXT,
            FOREIGN KEY(lead_id) REFERENCES leads(lead_id)
        );

        CREATE TABLE IF NOT EXISTS objections (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id         TEXT,
            objection_text  TEXT,
            objection_type  TEXT,
            rebuttal_used   TEXT,
            outcome         TEXT,
            logged_at       TEXT,
            FOREIGN KEY(lead_id) REFERENCES leads(lead_id)
        );
    """)
    conn.commit()
    conn.close()


# ── Lead CRUD ─────────────────────────────────────────────────

def upsert_lead(lead_data: dict) -> str:
    """Insert or update a lead. Returns lead_id."""
    init_database()
    lead_id = lead_data.get("lead_id")
    now = datetime.now().isoformat()

    conn = get_connection()
    c = conn.cursor()

    if not lead_id and lead_data.get("email"):
        existing_by_email = c.execute(
            "SELECT lead_id FROM leads WHERE email = ?", (lead_data.get("email"),)
        ).fetchone()
        if existing_by_email:
            lead_id = existing_by_email[0]

    if not lead_id:
        lead_id = f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:18]}"

    existing = c.execute("SELECT lead_id FROM leads WHERE lead_id=?", (lead_id,)).fetchone()
    if existing:
        c.execute("""
            UPDATE leads SET
                full_name=?, role=?, email=?, phone=?, company=?, industry=?,
                website=?, budget=?, source=?, notes=?, pipeline_stage=?,
                lead_temperature=?, composite_score=?, deal_probability=?,
                estimated_deal_size=?, assigned_to=?, updated_at=?
            WHERE lead_id=?
        """, (
            lead_data.get("full_name"), lead_data.get("role"), lead_data.get("email"),
            lead_data.get("phone"), lead_data.get("company"), lead_data.get("industry"),
            lead_data.get("website"), lead_data.get("budget"), lead_data.get("source"),
            lead_data.get("notes"), lead_data.get("pipeline_stage", "New Lead"),
            lead_data.get("lead_temperature", "Cold"),
            lead_data.get("composite_score", 0), lead_data.get("deal_probability", 0),
            lead_data.get("estimated_deal_size"), lead_data.get("assigned_to", "Unassigned"),
            now, lead_id
        ))
    else:
        c.execute("""
            INSERT INTO leads (lead_id, full_name, role, email, phone, company, industry,
                website, budget, source, notes, pipeline_stage, lead_temperature,
                composite_score, deal_probability, estimated_deal_size, assigned_to,
                created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            lead_id, lead_data.get("full_name"), lead_data.get("role"),
            lead_data.get("email"), lead_data.get("phone"), lead_data.get("company"),
            lead_data.get("industry"), lead_data.get("website"), lead_data.get("budget"),
            lead_data.get("source"), lead_data.get("notes"),
            lead_data.get("pipeline_stage", "New Lead"),
            lead_data.get("lead_temperature", "Cold"),
            lead_data.get("composite_score", 0), lead_data.get("deal_probability", 0),
            lead_data.get("estimated_deal_size"), lead_data.get("assigned_to", "Unassigned"),
            now, now
        ))
    conn.commit()
    conn.close()
    return lead_id


def update_lead_stage(lead_id: str, stage: str, temperature: str = None, score: int = None) -> bool:
    init_database()
    conn = get_connection()
    c = conn.cursor()
    updates = ["pipeline_stage=?", "updated_at=?"]
    values = [stage, datetime.now().isoformat()]
    if temperature:
        updates.append("lead_temperature=?"); values.append(temperature)
    if score is not None:
        updates.append("composite_score=?"); values.append(score)
    values.append(lead_id)
    c.execute(f"UPDATE leads SET {', '.join(updates)} WHERE lead_id=?", values)
    conn.commit()
    conn.close()
    return True


def get_lead(lead_id: str) -> Optional[Dict]:
    init_database()
    conn = get_connection()
    row = conn.execute("SELECT * FROM leads WHERE lead_id=?", (lead_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_leads(stage: str = None, temperature: str = None, limit: int = 100) -> List[Dict]:
    init_database()
    conn = get_connection()
    query = "SELECT * FROM leads"
    filters, vals = [], []
    if stage:
        filters.append("pipeline_stage=?"); vals.append(stage)
    if temperature:
        filters.append("lead_temperature=?"); vals.append(temperature)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += f" ORDER BY created_at DESC LIMIT {limit}"
    rows = conn.execute(query, vals).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def estimate_deal_amount(value) -> Optional[float]:
    """Read a numeric deal estimate from a CRM field; return None when absent."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower().replace(",", "")
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*(k|m|thousand|million)?", text)
    if len(matches) == 2 and re.search(r"\d\s*[-–]\s*\d", text):
        first, second = matches
        if not first[1] and second[1]:
            matches[0] = (first[0], second[1])
    amounts = []
    for number, suffix in matches:
        multiplier = 1_000 if suffix in ("k", "thousand") else 1_000_000 if suffix in ("m", "million") else 1
        amounts.append(float(number) * multiplier)
    amounts = [amount for amount in amounts if amount > 0]
    return sum(amounts) / len(amounts) if amounts else None


def get_pipeline_stats() -> Dict:
    init_database()
    conn = get_connection()
    by_stage = {}
    for row in conn.execute("SELECT pipeline_stage, COUNT(*) as cnt FROM leads GROUP BY pipeline_stage"):
        by_stage[row["pipeline_stage"]] = row["cnt"]
    by_temp = {}
    for row in conn.execute("SELECT lead_temperature, COUNT(*) as cnt FROM leads GROUP BY lead_temperature"):
        by_temp[row["lead_temperature"]] = row["cnt"]
    total = conn.execute("SELECT COUNT(*) as cnt FROM leads").fetchone()["cnt"]
    avg_score = conn.execute("SELECT AVG(composite_score) as avg FROM leads").fetchone()["avg"] or 0
    conn.close()
    return {
        "total_leads": total,
        "by_stage": by_stage,
        "by_temperature": by_temp,
        "avg_score": round(avg_score, 1),
        "hot_leads": by_temp.get("Hot", 0),
        "warm_leads": by_temp.get("Warm", 0),
        "cold_leads": by_temp.get("Cold", 0)
    }


# ── Research Storage ───────────────────────────────────────────

def save_research(lead_id: str, intelligence: dict):
    init_database()
    conn = get_connection()
    conn.execute("""
        INSERT INTO research_results (lead_id, intelligence, researched_at)
        VALUES (?, ?, ?)
    """, (lead_id, json.dumps(intelligence), datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_research(lead_id: str) -> Optional[Dict]:
    init_database()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM research_results WHERE lead_id=? ORDER BY researched_at DESC LIMIT 1",
        (lead_id,)
    ).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["intelligence"] = json.loads(d["intelligence"])
        return d
    return None


# ── Qualification Storage ──────────────────────────────────────

def save_qualification(lead_id: str, qualification: dict):
    init_database()
    conn = get_connection()
    conn.execute("""
        INSERT INTO qualification_results (lead_id, bant_scores, qualification, qualified_at)
        VALUES (?, ?, ?, ?)
    """, (
        lead_id,
        json.dumps(qualification.get("bant_scores", {})),
        json.dumps(qualification),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


# ── Email Storage ──────────────────────────────────────────────

def save_email(lead_id: str, email_type: str, email_data: dict) -> int:
    init_database()
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO emails (lead_id, email_type, subject_a, subject_b, body_html,
            plain_text, linkedin_msg, cta, reply_rate_est, written_at)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        lead_id, email_type,
        email_data.get("subject_line_a"), email_data.get("subject_line_b"),
        email_data.get("email_body"), email_data.get("plain_text_version"),
        email_data.get("linkedin_message"), email_data.get("cta"),
        email_data.get("estimated_reply_rate"),
        datetime.now().isoformat()
    ))
    email_id = c.lastrowid
    conn.commit()
    conn.close()
    return email_id


def get_emails_for_lead(lead_id: str) -> List[Dict]:
    init_database()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM emails WHERE lead_id=? ORDER BY written_at DESC", (lead_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_email_sent(email_id: int):
    init_database()
    conn = get_connection()
    conn.execute(
        "UPDATE emails SET sent=1, sent_at=? WHERE id=?",
        (datetime.now().isoformat(), email_id)
    )
    conn.commit()
    conn.close()


# ── Activity Log ──────────────────────────────────────────────

def log_activity(lead_id: str, activity_type: str, description: str, outcome: str = "", performer: str = "SalesAI"):
    init_database()
    conn = get_connection()
    conn.execute("""
        INSERT INTO activities (lead_id, activity_type, description, outcome, performed_by, created_at)
        VALUES (?,?,?,?,?,?)
    """, (lead_id, activity_type, description, outcome, performer, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_activities(lead_id: str) -> List[Dict]:
    init_database()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM activities WHERE lead_id=? ORDER BY created_at DESC", (lead_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Meeting Storage ────────────────────────────────────────────

def save_meeting(lead_id: str, meeting_data: dict) -> int:
    init_database()
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO meetings (lead_id, title, scheduled_at, duration_minutes,
            meeting_link, status, notes, created_at)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        lead_id,
        meeting_data.get("title", "Discovery Call"),
        meeting_data.get("scheduled_at"),
        meeting_data.get("duration_minutes", 30),
        meeting_data.get("meeting_link", ""),
        meeting_data.get("status", "Scheduled"),
        meeting_data.get("notes", ""),
        datetime.now().isoformat()
    ))
    mid = c.lastrowid
    conn.commit()
    conn.close()
    return mid


def get_meetings(lead_id: str) -> List[Dict]:
    init_database()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM meetings WHERE lead_id=? ORDER BY scheduled_at", (lead_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Objection Log ──────────────────────────────────────────────

def log_objection(lead_id: str, objection_text: str, obj_type: str, rebuttal: str, outcome: str = ""):
    init_database()
    conn = get_connection()
    conn.execute("""
        INSERT INTO objections (lead_id, objection_text, objection_type, rebuttal_used, outcome, logged_at)
        VALUES (?,?,?,?,?,?)
    """, (lead_id, objection_text, obj_type, rebuttal, outcome, datetime.now().isoformat()))
    conn.commit()
    conn.close()


# Initialize on import
init_database()
