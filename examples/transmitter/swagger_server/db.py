# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

from typing import Any, Dict

import contextlib
import json
import logging
import os
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Union

from swagger_server.events import SecurityEvent
from swagger_server.encoder import JSONEncoder
from swagger_server.errors import StreamDoesNotExist, SubjectNotInStream
from swagger_server.models import Status


CREATE_STREAMS_SQL = """
CREATE TABLE IF NOT EXISTS streams (
    client_id TEXT PRIMARY KEY,
    stream_data TEXT
)
"""

CREATE_SUBJECTS_SQL = """
CREATE TABLE IF NOT EXISTS subjects (
    client_id TEXT,
    email TEXT,
    status TEXT,
    FOREIGN KEY(client_id) REFERENCES streams(client_id),
    PRIMARY KEY(client_id, email)
)
"""

CREATE_SETS_SQL = """
CREATE TABLE IF NOT EXISTS SETs (
    client_id TEXT NOT NULL,
    jti TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    event TEXT NOT NULL,
    FOREIGN KEY(client_id) REFERENCES streams(client_id),
    PRIMARY KEY(client_id, jti)
)
"""


@contextlib.contextmanager
def connection() -> sqlite3.Connection:
    """Yield a connection that is guaranteed to close"""
    db_path = os.environ["DB_PATH"]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()


def create(drop=False):
    if drop:
        logging.warning("Dropping database")
        db_path = Path(os.environ["DB_PATH"])
        db_path.unlink()

    logging.info("Creating database")
    with connection() as conn:
        with conn:
            conn.execute(CREATE_STREAMS_SQL)
            conn.execute(CREATE_SUBJECTS_SQL)
            conn.execute(CREATE_SETS_SQL)


def stream_exists(client_id: str) -> bool:
    """Get a client_id info based on a token"""
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM streams WHERE client_id=?",
            (client_id,)
        ).fetchone()

        return row is not None


def save_stream(client_id: str, stream_data: str) -> None:
    """Saves a stream (minus subjects and events) to the db"""
    with connection() as conn:
        # open a transaction and commit if successful
        with conn:
            conn.execute(
                "REPLACE INTO streams VALUES (?, ?)", (client_id, stream_data)
            )


def load_stream(client_id: str) -> Dict[str, Any]:
    """Load the data needed to create a stream from the database"""
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM streams WHERE client_id=?",
            (client_id,)
        ).fetchone()

        if row:
            return json.loads(row["stream_data"])
        else:
            raise StreamDoesNotExist()


def get_stream_ids() -> List[str]:
    """Load the client id for all streams"""
    with connection() as conn:
        rows = conn.execute("SELECT client_id from streams").fetchall()
        return [row["client_id"] for row in rows]


def add_subject(client_id: str, email: str) -> None:
    """Add a subject to a stream"""
    with connection() as conn:
        with conn:
            conn.execute(
                "INSERT INTO subjects VALUES (?, ?, ?)",
                (client_id, email, Status.enabled.value)
            )


def set_subject_status(client_id: str, email: str, status: Status) -> None:
    """Set a subject's status"""
    with connection() as conn:
        with conn:
            conn.execute("""
                UPDATE subjects
                SET 
                    status = ?
                WHERE
                    client_id = ? AND
                    email = ?
                """,
                (status.value, client_id, email)
            )
        if conn.total_changes != 1:
            raise SubjectNotInStream(email)


def get_subject_status(client_id: str, email: str) -> Status:
    """Get a subject's status"""
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM subjects WHERE client_id=? AND email=?",
            (client_id, email)
        ).fetchone()

        if row:
            return Status(row["status"])
        else:
            raise SubjectNotInStream(email)


def remove_subject(client_id: str, email: str) -> None:
    """Remove a subject from a stream"""
    with connection() as conn:
        with conn:
            conn.execute(
                "DELETE FROM subjects WHERE client_id=? AND email=?",
                (client_id, email)
            )


def delete_subjects(client_id: str) -> None:
    """Delete all subjects for a stream"""
    with connection() as conn:
        with conn:
            conn.execute(
                "DELETE FROM subjects WHERE client_id=?",
                (client_id,)
            )


def add_set(client_id: str, SET: SecurityEvent) -> None:
    """Add a SET to the stream"""
    with connection() as conn:
        with conn:
            conn.execute(
                "INSERT INTO SETs VALUES (?, ?, ?, ?)",
                (client_id, SET.jti, SET.iat, JSONEncoder().encode(SET))
            )


def delete_SETs(client_id: str, jtis: Optional[List[str]]=None) -> None:
    """Delete SETs from the stream, based on their jtis"""
    sql = "DELETE FROM SETs WHERE client_id=?"
    if jtis:
        qmarks = ",".join(["?"] * len(jtis))
        sql += f" AND jti IN ({qmarks})"

    with connection() as conn:
        with conn:
            conn.execute(sql, (client_id, *jtis) if jtis else (client_id, ))


def count_SETs(client_id: str) -> int:
    """How many SETs are in the stream?"""
    with connection() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM SETs WHERE client_id = ?",
            (client_id,)
        ).fetchone()[0]


def get_SETs(client_id: str, max_events: Optional[int]=None) -> List[SecurityEvent]:
    """Get up to max_events SETs from the stream"""
    if max_events is not None and max_events <= 0:
        return []

    sql = "SELECT * FROM SETs WHERE client_id=? ORDER BY timestamp"

    if max_events is not None:
        sql += f" LIMIT {max_events}"

    with connection() as conn:
        results = conn.execute(sql, (client_id, )).fetchall()
        return [
            SecurityEvent.parse_obj(json.loads(r["event"]))
            for r in results
        ]
