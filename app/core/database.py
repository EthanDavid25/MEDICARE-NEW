"""MEDICARE SQLite database layer."""
import sqlite3
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("medicare.database")

_SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name        TEXT NOT NULL,
    date_of_birth       TEXT,
    biological_sex      TEXT CHECK(biological_sex IN ('male','female','other','prefer_not_to_say')),
    blood_group         TEXT,
    known_allergies     TEXT,
    chronic_conditions  TEXT,
    current_medications TEXT,
    emergency_contact   TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    is_deleted          INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS assessments (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id        INTEGER NOT NULL REFERENCES patients(id),
    session_id        TEXT NOT NULL UNIQUE,
    started_at        TEXT NOT NULL,
    completed_at      TEXT,
    urgency_category  INTEGER CHECK(urgency_category BETWEEN 1 AND 4),
    urgency_label     TEXT,
    triage_version    TEXT,
    rules_triggered   TEXT,
    explanation       TEXT,
    raw_input         TEXT,
    warnings_found    TEXT,
    is_deleted        INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS symptom_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id   INTEGER NOT NULL REFERENCES assessments(id),
    patient_id      INTEGER NOT NULL REFERENCES patients(id),
    symptom_code    TEXT NOT NULL,
    symptom_name    TEXT NOT NULL,
    reported_at     TEXT NOT NULL,
    duration_value  INTEGER,
    duration_unit   TEXT CHECK(duration_unit IN ('hours','days','weeks','months')),
    severity        INTEGER CHECK(severity BETWEEN 1 AND 10),
    progression     TEXT CHECK(progression IN ('improving','unchanged','worsening','unknown')),
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS symptom_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      INTEGER NOT NULL REFERENCES patients(id),
    symptom_code    TEXT NOT NULL,
    symptom_name    TEXT NOT NULL,
    recorded_at     TEXT NOT NULL,
    duration_value  INTEGER,
    duration_unit   TEXT,
    severity        INTEGER CHECK(severity BETWEEN 1 AND 10),
    progression     TEXT CHECK(progression IN ('improving','unchanged','worsening','unknown')),
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS followup_answers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL REFERENCES assessments(id),
    question_id   TEXT NOT NULL,
    question_text TEXT NOT NULL,
    answer_code   TEXT NOT NULL,
    answer_text   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS triage_rules (
    rule_id                TEXT PRIMARY KEY,
    version                TEXT NOT NULL,
    description            TEXT NOT NULL,
    source                 TEXT NOT NULL,
    conditions_json        TEXT NOT NULL,
    urgency_category       INTEGER NOT NULL,
    explanation            TEXT NOT NULL,
    test_case_json         TEXT,
    clinical_review_status TEXT NOT NULL DEFAULT 'NOT_REVIEWED',
    is_active              INTEGER NOT NULL DEFAULT 1,
    created_at             TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS facilities (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    facility_code    TEXT UNIQUE,
    name             TEXT NOT NULL,
    facility_type    TEXT NOT NULL,
    address          TEXT,
    city             TEXT,
    state            TEXT,
    country          TEXT,
    phone            TEXT,
    emergency_phone  TEXT,
    has_emergency    INTEGER DEFAULT 0,
    operating_hours  TEXT,
    services         TEXT,
    verified         INTEGER DEFAULT 0,
    data_source      TEXT,
    last_updated     TEXT,
    notes            TEXT
);

CREATE TABLE IF NOT EXISTS medical_references (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_code     TEXT UNIQUE,
    category     TEXT NOT NULL,
    title        TEXT NOT NULL,
    summary      TEXT,
    content      TEXT,
    source       TEXT,
    url          TEXT,
    version      TEXT,
    last_updated TEXT
);

CREATE TABLE IF NOT EXISTS dataset_metadata (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_name      TEXT NOT NULL UNIQUE,
    source            TEXT,
    version           TEXT,
    acquired_date     TEXT,
    last_updated      TEXT,
    license_info      TEXT,
    validation_status TEXT DEFAULT 'UNVALIDATED',
    record_count      INTEGER,
    notes             TEXT
);

CREATE TABLE IF NOT EXISTS app_settings (
    key        TEXT PRIMARY KEY,
    value      TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS downloaded_handovers (
    id                TEXT PRIMARY KEY,
    session_id        TEXT,
    patient_id        INTEGER,
    patient_name      TEXT,
    title             TEXT,
    main_symptoms     TEXT,
    pain_severity     INTEGER,
    triage_category   INTEGER,
    triage_label      TEXT,
    filename          TEXT NOT NULL,
    file_path         TEXT NOT NULL,
    file_size         INTEGER DEFAULT 0,
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    downloaded_at     TEXT NOT NULL DEFAULT (datetime('now')),
    format            TEXT DEFAULT 'PDF',
    status            TEXT DEFAULT 'available'
);

CREATE TABLE IF NOT EXISTS audit_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type   TEXT NOT NULL,
    event_detail TEXT,
    occurred_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


class SQLiteDatabase:
    """
    Thread-safe SQLite database wrapper for MEDICARE.

    All queries are parameterised. PII must never be passed to log calls.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def initialize(self):
        """Create all tables and enable foreign key support."""
        conn = self._connect()
        conn.executescript(_SCHEMA_SQL)
        conn.commit()
        logger.info("Database schema initialized at %s", self.db_path)

    def close(self):
        """Close the database connection."""
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception as exc:
                logger.warning("Error closing database: %s", type(exc).__name__)
            finally:
                self._conn = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    # ------------------------------------------------------------------
    # Core query helpers
    # ------------------------------------------------------------------

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a parameterised SQL statement. Returns the cursor."""
        conn = self._connect()
        try:
            cursor = conn.execute(sql, params)
            conn.commit()
            return cursor
        except sqlite3.Error as exc:
            logger.error("DB execute error (%s): %s", type(exc).__name__, sql[:80])
            raise

    def fetchall(self, sql: str, params: tuple = ()) -> list:
        """Execute a SELECT and return a list of dicts."""
        conn = self._connect()
        try:
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as exc:
            logger.error("DB fetchall error (%s): %s", type(exc).__name__, sql[:80])
            raise

    def fetchone(self, sql: str, params: tuple = ()):
        """Execute a SELECT and return a single dict or None."""
        conn = self._connect()
        try:
            cursor = conn.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as exc:
            logger.error("DB fetchone error (%s): %s", type(exc).__name__, sql[:80])
            raise

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def insert(self, table: str, data: dict) -> int:
        """
        Insert a row into *table* using *data* (column→value mapping).
        Returns the lastrowid.
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"  # noqa: S608
        cursor = self.execute(sql, tuple(data.values()))
        return cursor.lastrowid

    def update(self, table: str, data: dict, where: str, where_params: tuple) -> int:
        """
        Update rows in *table*.
        *data*: columns to set.
        *where*: WHERE clause (without the keyword), e.g. "id = ?".
        *where_params*: parameters for the WHERE clause.
        Returns rowcount.
        """
        set_clause = ", ".join(f"{col} = ?" for col in data.keys())
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"  # noqa: S608
        cursor = self.execute(sql, tuple(data.values()) + where_params)
        return cursor.rowcount

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def log_audit_event(self, event_type: str, detail: str = ""):
        """
        Write a record to audit_log.
        IMPORTANT: Never pass patient PII as event_type or detail.
        """
        try:
            self.insert(
                "audit_log",
                {"event_type": event_type, "event_detail": detail},
            )
        except Exception as exc:
            # Audit failures must not crash the application
            logger.warning("Audit log write failed: %s", type(exc).__name__)
