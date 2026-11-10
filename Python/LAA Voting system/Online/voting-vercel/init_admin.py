#!/usr/bin/env python3
"""Create/reset a database admin account (run locally, NEVER on public web).

PowerShell:
  $env:DATABASE_URL = "postgresql://..."
  python init_admin.py --username admin
Prompts for a password and stores only a scrypt hash in the database.
"""
import argparse
import getpass
import os
from pathlib import Path
import psycopg
from werkzeug.security import generate_password_hash


def main():
    p = argparse.ArgumentParser(description="Create or reset an administrator")
    p.add_argument("--username", default="admin", help="Admin username (default: admin)")
    args = p.parse_args()
    username = args.username.strip()
    if not username or len(username) > 64:
        raise SystemExit("Username must contain between 1 and 64 characters.")
    first = getpass.getpass("Nové heslo administrátora (min. 14 znaků): ")
    if len(first) < 14:
        raise SystemExit("Heslo musí mít alespoň 14 znaků.")
    if getpass.getpass("Heslo znovu: ") != first:
        raise SystemExit("Hesla se neshodují.")
    if not os.environ.get("DATABASE_URL"):
        raise SystemExit("Nastavte proměnnou DATABASE_URL.")
    password_hash = generate_password_hash(first, method="scrypt")
    with psycopg.connect(os.environ["DATABASE_URL"]) as db:
        db.execute(Path(__file__).with_name("auth_schema.sql").read_text(encoding="utf-8"))
        existing = db.execute("SELECT id FROM admin_users WHERE lower(username)=lower(%s)",
                              (username,)).fetchone()
        if existing:
            db.execute("UPDATE admin_users SET username=%s, password_hash=%s, active=TRUE WHERE id=%s",
                       (username, password_hash, existing[0]))
            db.execute("DELETE FROM admin_sessions WHERE user_id=%s", (existing[0],))
            print("Heslo bylo změněno; staré relace byly odhlášeny.")
        else:
            db.execute("INSERT INTO admin_users(username,password_hash) VALUES(%s,%s)",
                       (username, password_hash))
            print("Účet vytvořen:", username)

if __name__ == "__main__":
    main()
