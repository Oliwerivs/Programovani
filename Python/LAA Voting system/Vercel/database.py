"""Request-scoped PostgreSQL connection, SQLite-compatible query facade."""
import contextvars
import os
import re
import psycopg

_current = contextvars.ContextVar("db_connection", default=None)


def connect():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not configured")
    return psycopg.connect(url, connect_timeout=15, prepare_threshold=None)


def begin(conn):
    return _current.set(conn)


def end(token):
    _current.reset(token)


def connection():
    conn = _current.get()
    if conn is None:
        raise RuntimeError("Database connection outside request")
    return conn


class Query:
    def __init__(self, cursor):
        self.cursor = cursor
    def fetchall(self):
        return self.cursor.fetchall()
    def fetchone(self):
        return self.cursor.fetchone()


class DBAdapter:
    def execute(self, sql, args=()):
        # All queries in this application use positional SQLite placeholders.
        statement = sql.replace("?", "%s")
        cursor = connection().execute(statement, args)
        return Query(cursor)
    def commit(self):
        connection().commit()
    def rollback(self):
        connection().rollback()

DB = DBAdapter()


def q(sql, args=()):
    return DB.execute(sql, args).fetchall()


def serialize_mutations():
    # Global transaction-scoped lock across all Vercel function instances.
    # Prevents simultaneous check-in, roster, open/close, and ballot races.
    connection().execute("SELECT pg_advisory_xact_lock(72918462)")


def duplicate_vote(vote_id, ballot_id):
    row = connection().execute(
        "INSERT INTO vote_cast(vote_id,ballot_id) VALUES(%s,%s) ON CONFLICT DO NOTHING RETURNING vote_id",
        (vote_id, ballot_id),
    ).fetchone()
    return row is not None
