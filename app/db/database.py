import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.core.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS api_keys (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    label                   TEXT NOT NULL,
    encrypted_key           TEXT NOT NULL,
    enabled                 INTEGER NOT NULL DEFAULT 1,
    is_current              INTEGER NOT NULL DEFAULT 0,
    -- Umbrales configurables por el admin, calcados de las 3 dimensiones
    -- que Google muestra en AI Studio (RPM / TPM / RPD). TPD es un extra
    -- opcional que Google no expone pero puede servir como techo propio.
    rpm_threshold           INTEGER,
    tpm_threshold           INTEGER,
    rpd_threshold           INTEGER,
    tpd_threshold           INTEGER,
    -- Contadores de ventana diaria (resetean por fecha UTC)
    request_count           INTEGER NOT NULL DEFAULT 0,
    prompt_token_count      INTEGER NOT NULL DEFAULT 0,
    candidates_token_count  INTEGER NOT NULL DEFAULT 0,
    total_token_count       INTEGER NOT NULL DEFAULT 0,
    last_reset_date         TEXT NOT NULL DEFAULT (date('now')),
    -- Contadores de ventana de minuto (resetean por minuto UTC)
    minute_request_count    INTEGER NOT NULL DEFAULT 0,
    minute_token_count      INTEGER NOT NULL DEFAULT 0,
    last_reset_minute       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M', 'now')),
    created_at              TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_api_keys_current
    ON api_keys(is_current) WHERE is_current = 1;
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    Path(settings.DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)
