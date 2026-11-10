"""Vercel entry point: Flask + Neon PostgreSQL."""
import csv
import io
import json
import os
import time
from flask import Flask, Response, request, jsonify
from database import connect, begin, end, serialize_mutations
from admin_auth import (get_session, log_in, log_out, cookie_name, cookie_is_secure,
                        SESSION_LIFETIME_SECONDS, secure_admin_mutation)
import voting_core as core

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

@app.after_request
def response_headers(resp):
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
    return resp


def authenticated_admin():
    return get_session(request)


def require_admin():
    session = authenticated_admin()
    if not session:
        raise PermissionError("Přihlaste se jako administrátor.")
    return session


def handle_db(fn, *, mutation=False):
    conn = connect()
    token = begin(conn)
    try:
        if mutation:
            serialize_mutations()
        result = fn()
        conn.commit()
        return result
    except core.AuthError as e:
        conn.rollback()
        return jsonify(error=str(e)), 403
    except PermissionError as e:
        conn.rollback()
        return jsonify(error=str(e)), 403
    except (ValueError, KeyError, TypeError) as e:
        conn.rollback()
        return jsonify(error=str(e)), 400
    except Exception:
        conn.rollback()
        app.logger.exception("Request error")
        return jsonify(error="Chyba serveru"), 500
    finally:
        end(token)
        conn.close()


@app.get("/")
def home():
    return Response(core.VOTER, content_type="text/html; charset=utf-8")

@app.get("/admin")
def admin():
    return Response(core.ADMIN, content_type="text/html; charset=utf-8")

@app.get("/screen")
def screen():
    return Response(core.SCREEN, content_type="text/html; charset=utf-8")

@app.get("/vysledky")
def results():
    return Response(core.RESULTS, content_type="text/html; charset=utf-8")

@app.get("/qr.js")
def qr():
    return Response(core.QRJS, content_type="application/javascript; charset=utf-8")

@app.get("/api/state")
def state():
    def do():
        data = core.state()
        data["url"] = os.environ.get("PUBLIC_URL", request.url_root)
        return jsonify(data)
    return handle_db(do)

@app.get("/api/auth/session")
def auth_session():
    def do():
        session = authenticated_admin()
        if not session:
            return jsonify(authenticated=False)
        return jsonify(authenticated=True, username=session["username"], csrf=session["csrf_token"])
    return handle_db(do)


@app.post("/api/auth/login")
def auth_login():
    def do():
        if not request.is_json:
            return jsonify(error="Očekávána JSON data."), 415
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="Neplatná data."), 400
        username = str(data.get("username", ""))[:128].strip()
        password = str(data.get("password", ""))[:1024]
        result, issue = log_in(username, password, request.remote_addr or "")
        if issue:
            return jsonify(error=issue), 429 if "pokusů" in issue else 401
        resp = jsonify(ok=True, username=result["username"], csrf=result["csrf_token"])
        resp.set_cookie(cookie_name(request), result["token"], max_age=SESSION_LIFETIME_SECONDS,
                        secure=cookie_is_secure(request), httponly=True, samesite="Strict", path="/")
        return resp
    return handle_db(do, mutation=True)


@app.post("/api/auth/logout")
def auth_logout():
    def do():
        session = require_admin()
        secure_admin_mutation(request, session)
        log_out(session)
        resp = jsonify(ok=True)
        resp.delete_cookie(cookie_name(request), path="/", secure=cookie_is_secure(request),
                           httponly=True, samesite="Strict")
        return resp
    return handle_db(do, mutation=True)


@app.get("/api/admin/<path:action>")
def admin_get(action):
    def do():
        require_admin()
        if action == "status": return jsonify(core.admin_status())
        if action == "code": return jsonify(code=core.vote_code())
        if action == "roster": return jsonify(core.roster_search(request.args.get("q", "")))
        if action == "export":
            return Response("\ufeff" + core.export(), content_type="text/csv; charset=utf-8",
                            headers={"Content-Disposition": "attachment; filename=hlasovani.csv"})
        if action == "export.xlsx":
            return Response(core.xlsx_export(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            headers={"Content-Disposition": 'attachment; filename="hlasovani-%s.xlsx"' % time.strftime("%Y-%m-%d")})
        return jsonify(error="Nenalezeno"), 404
    return handle_db(do)

@app.post("/api/<path:action>")
def api_post(action):
    def do():
        if not request.is_json: raise ValueError("Očekávána JSON data")
        data = request.get_json(silent=True)
        if not isinstance(data, dict): raise ValueError("Neplatná data")
        lic = str(data.get("licence", "")).strip()
        pin = str(data.get("pin", ""))
        if action == "me": return jsonify(core.me(lic, pin))
        if action == "confirm":
            core.confirm(lic, pin, str(data.get("code", "")).strip())
            return jsonify(ok=1)
        if action == "cast":
            core.cast(lic, pin, data.get("ballot_id"), data.get("choice"))
            return jsonify(ok=1)
        if action.startswith("admin/"):
            secure_admin_mutation(request, require_admin())
            cmd = action[len("admin/"):]
            funcs = {"checkin": core.checkin, "checkout": core.checkout,
                     "open": core.open_vote, "close": core.close_vote,
                     "roster": lambda d: core.roster_replace(core.parse_csv(str(d.get("csv", ""))))}
            if cmd not in funcs: return jsonify(error="Nenalezeno"), 404
            return jsonify(funcs[cmd](data) or {"ok": 1})
        return jsonify(error="Nenalezeno"), 404
    return handle_db(do, mutation=action != "me")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8000")))
