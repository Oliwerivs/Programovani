"""Admin authentication: PostgreSQL-backed server sessions, no keys in URLs."""
import hashlib
import hmac
import secrets

from werkzeug.security import check_password_hash
from database import connection

SESSION_LIFETIME_SECONDS = 8 * 60 * 60
SESSION_COOKIE = "__Host-voting_admin"
DEV_COOKIE = "voting_admin_local"


def cookie_is_secure(request):
    # Production must use HTTPS. HTTP is allowed only for local development.
    host = request.host.split(":")[0].lower()
    return host not in ("127.0.0.1", "localhost")


def cookie_name(request):
    return SESSION_COOKIE if cookie_is_secure(request) else DEV_COOKIE


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def get_session(request):
    token = request.cookies.get(cookie_name(request), "")
    if not (32 <= len(token) <= 256):
        return None
    row = connection().execute(
        "SELECT s.token_hash, s.csrf_token, u.username "
        "FROM admin_sessions s JOIN admin_users u ON u.id=s.user_id "
        "WHERE s.token_hash=%s AND s.expires_at > now() AND u.active=TRUE",
        (digest(token),),
    ).fetchone()
    return {"token_hash": row[0], "csrf_token": row[1], "username": row[2]} if row else None


def secure_admin_mutation(request, session):
    supplied = request.headers.get("X-CSRF-Token", "")
    if not supplied or not hmac.compare_digest(supplied, session["csrf_token"]):
        raise PermissionError("Chybí nebo je neplatný CSRF token. Přihlaste se znovu.")
    # Non-simple JSON request + same-origin policy prevents cookie-based cross-site POSTs.
    if not request.is_json:
        raise ValueError("Očekávána JSON data")


def _attempt_keys(username, ip):
    return ("user:" + digest(username.casefold()), "ip:" + digest(ip))


def log_in(username, password, ip):
    """Call under the global transaction mutation lock. On failure return an error,
    not an exception, so the abuse-limit records get committed.
    """
    db = connection()
    db.execute("DELETE FROM admin_login_attempts WHERE occurred_at < now() - interval '1 day'")
    keys = _attempt_keys(username, ip)
    counts = db.execute(
        "SELECT key, COUNT(*) FROM admin_login_attempts "
        "WHERE key = ANY(%s) AND occurred_at > now() - interval '15 minutes' "
        "GROUP BY key", (list(keys),),
    ).fetchall()
    # Throttle by address and by account. A somewhat higher per-account limit
    # reduces the risk of a trivial deliberate lockout of the known admin user.
    if any((n >= 12 if k.startswith("ip:") else n >= 50) for k, n in counts):
        return None, "Příliš mnoho chybných pokusů. Zkuste to za 15 minut."

    user = db.execute(
        "SELECT id, username, password_hash FROM admin_users "
        "WHERE lower(username) = lower(%s) AND active=TRUE", (username,),
    ).fetchone()
    valid = bool(user and password and check_password_hash(user[2], password))
    if not valid:
        db.executemany("INSERT INTO admin_login_attempts (key) VALUES (%s)",
                       [(k,) for k in keys])
        return None, "Neplatné uživatelské jméno nebo heslo."
    db.execute("DELETE FROM admin_login_attempts WHERE key=%s", (keys[0],))
    # Deleting expired sessions here avoids accumulating old tokens.
    db.execute("DELETE FROM admin_sessions WHERE expires_at < now()")
    token = secrets.token_urlsafe(48)
    csrf = secrets.token_urlsafe(32)
    db.execute(
        "INSERT INTO admin_sessions(token_hash,user_id,csrf_token,expires_at) "
        "VALUES(%s,%s,%s,now() + interval '8 hours')",
        (digest(token), user[0], csrf),
    )
    return {"username": user[1], "token": token, "csrf_token": csrf}, None


def log_out(session):
    connection().execute("DELETE FROM admin_sessions WHERE token_hash=%s",
                         (session["token_hash"],))
