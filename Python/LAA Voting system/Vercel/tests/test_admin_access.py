"""Run after pip install -r requirements.txt: python -m unittest discover -s tests"""
import unittest
from unittest.mock import patch
from app import app


class FakeConnection:
    def commit(self): pass
    def rollback(self): pass
    def close(self): pass


class AdminAccessTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.conn = FakeConnection()
        self.patch_connect = patch("app.connect", return_value=self.conn)
        self.patch_lock = patch("app.serialize_mutations")
        self.patch_connect.start()
        self.patch_lock.start()
        self.addCleanup(self.patch_connect.stop)
        self.addCleanup(self.patch_lock.stop)

    def test_administration_is_protected_without_cookie(self):
        with patch("app.get_session", return_value=None):
            self.assertEqual(self.client.get("/api/admin/status").status_code, 403)
            self.assertEqual(self.client.get("/api/admin/export").status_code, 403)
            self.assertEqual(self.client.get("/api/admin/code").status_code, 403)
            self.assertEqual(self.client.post("/api/admin/open", json={}).status_code, 403)

    def test_successful_login_issues_http_only_cookie_not_url_key(self):
        credentials = {"username": "admin", "password": "example-test-password"}
        data = {"username": "admin", "token": "very-long-random-session-token", "csrf_token": "secret-csrf"}
        with patch("app.log_in", return_value=(data, None)):
            resp = self.client.post("/api/auth/login", json=credentials,
                                    base_url="https://hlasy.example.cz")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("HttpOnly", resp.headers["Set-Cookie"])
        self.assertIn("Secure", resp.headers["Set-Cookie"])
        self.assertIn("SameSite=Strict", resp.headers["Set-Cookie"])
        self.assertIn("__Host-voting_admin", resp.headers["Set-Cookie"])
        self.assertNotIn("?key=", resp.get_data(as_text=True))

    def test_invalid_login_does_not_issue_cookie(self):
        with patch("app.log_in", return_value=(None, "Neplatné heslo.")):
            resp = self.client.post("/api/auth/login", json={"username": "admin", "password": "bad"})
        self.assertEqual(resp.status_code, 401)
        self.assertNotIn("Set-Cookie", resp.headers)

    def test_admin_mutation_requires_csrf(self):
        session = {"username": "admin", "token_hash": "hash", "csrf_token": "right-csrf"}
        with patch("app.get_session", return_value=session):
            resp = self.client.post("/api/admin/open", json={"title":"Question","options":["yes","no"]})
            self.assertEqual(resp.status_code, 403)

    def test_log_out_revokes_session(self):
        session = {"username": "admin", "token_hash": "hash", "csrf_token": "right-csrf"}
        with patch("app.get_session", return_value=session), patch("app.log_out") as revoke:
            resp = self.client.post("/api/auth/logout", json={}, headers={"X-CSRF-Token":"right-csrf"})
        self.assertEqual(resp.status_code, 200)
        revoke.assert_called_once_with(session)


if __name__ == "__main__":
    unittest.main()
