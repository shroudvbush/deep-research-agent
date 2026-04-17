import sqlite3, json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "research_history.db"


def _get_conn():
    Path(__file__).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS research_history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at   TEXT    NOT NULL,
            topic        TEXT    NOT NULL,
            constraints_ TEXT    DEFAULT '',
            category     TEXT    DEFAULT 'research',
            sources      TEXT    DEFAULT '[]',
            tasks_json   TEXT    DEFAULT '[]',
            report_json  TEXT    DEFAULT '{}',
            status       TEXT    DEFAULT 'completed'
        )
        """
    )
    try:
        conn.execute("ALTER TABLE research_history ADD COLUMN category TEXT DEFAULT 'research'")
    except Exception:
        pass
    conn.commit()
    conn.close()


def save_record(
    topic: str,
    constraints: str,
    sources: list,
    tasks: list,
    report: dict,
    status: str = "completed",
    category: str = "research",
) -> int:
    conn = _get_conn()
    cur = conn.execute(
        """
        INSERT INTO research_history (created_at, topic, constraints_, category, sources, tasks_json, report_json, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(timespec="seconds"),
            topic,
            constraints,
            category,
            json.dumps(sources, ensure_ascii=False),
            json.dumps(tasks, ensure_ascii=False),
            json.dumps(report, ensure_ascii=False),
            status,
        ),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def get_all_history(category: str = "", limit: int = 50) -> list:
    conn = _get_conn()
    if category:
        rows = conn.execute(
            "SELECT * FROM research_history WHERE category=? ORDER BY created_at DESC LIMIT ?",
            (category, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM research_history ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_record(rid: int) -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM research_history WHERE id = ?", (rid,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_record(rid: int) -> bool:
    conn = _get_conn()
    cur = conn.execute("DELETE FROM research_history WHERE id = ?", (rid,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


init_db()
