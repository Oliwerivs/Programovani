"""One-time import from existing SQLite databases; requires DATABASE_URL.

Usage: python migrate.py /path/to/voting.db [/path/to/clenove.db]
Does not overwrite a populated Neon database. Never commit the input DBs.
"""
import csv
import os
import sqlite3
import sys
from pathlib import Path
import psycopg

TABLES = ["members", "ballots", "votes", "vote_cast", "tally", "open_choices", "confirmed", "roster"]
COLUMNS = {
    "members": ["id", "licence", "name", "present", "pin"],
    "ballots": ["id", "member_id", "label", "club"],
    "votes": ["id", "title", "secret", "options", "status", "eligible", "code", "live"],
    "vote_cast": ["vote_id", "ballot_id"],
    "tally": ["vote_id", "choice", "n"],
    "open_choices": ["vote_id", "ballot_id", "choice"],
    "confirmed": ["vote_id", "member_id"],
    "roster": ["licence", "name", "club", "voting"],
}

def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python migrate.py voting.db [clenove.db]")
    source = Path(sys.argv[1])
    if not source.exists(): raise SystemExit("Input SQLite file not found")
    with sqlite3.connect(source) as old, psycopg.connect(os.environ["DATABASE_URL"]) as pg:
        # Always create missing tables in the same transaction.
        pg.execute(Path(__file__).with_name("schema.sql").read_text())
        if any(pg.execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone() for table in TABLES):
            raise SystemExit("Target DB is NOT empty. Import cancelled to prevent duplicate/corrupted votes.")
        for table in TABLES:
            names = COLUMNS[table]
            source_table = "cast" if table == "vote_cast" else table
            available = {row[1] for row in old.execute(f"PRAGMA table_info({source_table})")}
            cols = [col for col in names if col in available]
            rows = old.execute(f"SELECT {','.join(cols)} FROM {source_table}").fetchall()
            if rows:
                sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})"
                with pg.cursor() as c: c.executemany(sql, rows)
            print(f"{table}: {len(rows)} records")
        # Optional fallback when voting.db contains no roster.
        if len(sys.argv) > 2 and not pg.execute("SELECT 1 FROM roster LIMIT 1").fetchone():
            with sqlite3.connect(sys.argv[2]) as members:
                rows = members.execute("SELECT licence,jmeno,klub,hlasuje FROM clenove").fetchall()
                for lic, name, club, voting in rows:
                    pg.execute("INSERT INTO roster VALUES(%s,%s,%s,%s)", (lic,name,club,int(voting)))
                print(f"roster from clenove.db: {len(rows)}")
        for table in ("members", "ballots", "votes"):
            pg.execute(f"SELECT setval(pg_get_serial_sequence('{table}','id'), GREATEST((SELECT COALESCE(MAX(id),0) FROM {table}), 1), (SELECT COUNT(*) > 0 FROM {table}))")
    print("Import complete.")

if __name__ == '__main__': main()
