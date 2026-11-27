import base64
import http.client
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from http_api import make_server
from persistent import PersistentControlPlane
from storage import SQLiteStore
from entitlements import Gateway


ENROLL = "test-enrollment-secret"
ADMIN = "test-admin-secret"
PUBLIC_KEY = base64.b64encode(bytes(range(32))).decode()


class HTTPAPITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        store = SQLiteStore(Path(self.temp.name) / "test.sqlite3")
        self.control = PersistentControlPlane(store)
        self.server = make_server(
            "127.0.0.1", 0, self.control, ENROLL, ADMIN
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.thread.start()
        self.base = "http://127.0.0.1:" + str(
            self.server.server_address[1]
        )
        self.device_token = None
        self.device_id = None

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.temp.cleanup()

    def request(self, method, path, data=None, token=None):
        body = None if data is None else json.dumps(data).encode()
        headers = {}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = "Bearer " + token
        req = urllib.request.Request(
            self.base + path, data=body, headers=headers, method=method
        )
        try:
            response = urllib.request.urlopen(req, timeout=3)
        except urllib.error.HTTPError as exc:
            response = exc

        try:
            status = response.code
            payload = json.loads(response.read())
            return status, payload
        finally:
            response.close()

    def raw_request(self, method, path, headers=(), body=None):
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_address[1], timeout=3
        )
        try:
            connection.putrequest(method, path)
            for name, value in headers:
                connection.putheader(name, value)
            connection.endheaders(body)
            response = connection.getresponse()
            try:
                return response.status, json.loads(response.read())
            finally:
                response.close()
        finally:
            connection.close()

    def enroll(self):
        status, result = self.request(
            "POST", "/v1/devices/enroll",
            {"device_public_key": PUBLIC_KEY, "platform": "android"},
            ENROLL,
        )
        self.assertEqual(status, 201)
        self.device_token = result["device_token"]
        self.device_id = result["device_id"]
        return result

    def test_unsupported_methods_return_json_405(self):
        for method in ("PUT", "PATCH", "DELETE", "OPTIONS", "BREW"):
            with self.subTest(method=method):
                status, body = self.request(method, "/v1/health")
                self.assertEqual(status, 405)
                self.assertEqual(body["error"], "method not allowed")

    def test_missing_content_length_returns_411(self):
        status, body = self.raw_request(
            "POST", "/v1/devices/enroll",
            [
                ("Authorization", "Bearer " + ENROLL),
                ("Content-Type", "application/json"),
            ],
        )
        self.assertEqual(status, 411)
        self.assertEqual(body["error"], "Content-Length is required")

    def test_oversized_body_returns_413(self):
        body_data = b"x" * 16385
        status, body = self.raw_request(
            "POST", "/v1/devices/enroll",
            [
                ("Authorization", "Bearer " + ENROLL),
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(body_data))),
            ],
            body_data,
        )
        self.assertEqual(status, 413)
        self.assertEqual(
            body["error"], "request body exceeds the size limit"
        )

    def test_transfer_encoding_is_rejected(self):
        status, body = self.raw_request(
            "POST", "/v1/devices/enroll",
            [
                ("Authorization", "Bearer " + ENROLL),
                ("Content-Type", "application/json"),
                ("Transfer-Encoding", "chunked"),
            ],
        )
        self.assertEqual(status, 400)
        self.assertEqual(
            body["error"], "Transfer-Encoding is not supported"
        )

    def test_duplicate_content_length_is_rejected(self):
        status, body = self.raw_request(
            "POST", "/v1/devices/enroll",
            [
                ("Authorization", "Bearer " + ENROLL),
                ("Content-Type", "application/json"),
                ("Content-Length", "2"),
                ("Content-Length", "2"),
            ],
            b"{}",
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "duplicate Content-Length")

    def test_duplicate_json_keys_are_rejected_at_all_levels(self):
        bodies = (
            b'{"device_public_key":"x","device_public_key":"y","platform":"android"}',
            b'{"device_public_key":"x","platform":"android","extra":{"role":"user","role":"admin"}}',
        )

        for raw_body in bodies:
            with self.subTest(body=raw_body):
                status, body = self.raw_request(
                    "POST", "/v1/devices/enroll",
                    [
                        ("Authorization", "Bearer " + ENROLL),
                        ("Content-Type", "application/json"),
                        ("Content-Length", str(len(raw_body))),
                    ],
                    raw_body,
                )
                self.assertEqual(status, 400)
                self.assertEqual(
                    body["error"], "duplicate JSON object key"
                )

    def test_wrong_content_type_returns_415(self):
        status, body = self.raw_request(
            "POST", "/v1/devices/enroll",
            [
                ("Authorization", "Bearer " + ENROLL),
                ("Content-Type", "text/plain"),
                ("Content-Length", "2"),
            ],
            b"{}",
        )
        self.assertEqual(status, 415)
        self.assertEqual(
            body["error"], "Content-Type must be application/json"
        )

    def test_get_internal_failure_returns_generic_json_500(self):
        self.enroll()

        def simulate_failure():
            raise RuntimeError("private database failure detail")

        self.control.eligible_gateways = simulate_failure

        status, body = self.request(
            "GET", "/v1/gateways", token=self.device_token
        )

        self.assertEqual(status, 500)
        self.assertEqual(body, {"error": "internal server error"})
        self.assertNotIn("private database failure detail", str(body))

    def test_health_is_public(self):
        status, body = self.request("GET", "/v1/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_enrollment_requires_enrollment_token(self):
        status, _ = self.request(
            "POST", "/v1/devices/enroll",
            {"device_public_key": PUBLIC_KEY, "platform": "android"},
        )
        self.assertEqual(status, 401)

    def test_enrollment_returns_device_token_once(self):
        result = self.enroll()
        self.assertEqual(result["status"], "enrolled")
        self.assertTrue(result["device_token"])
        self.assertNotIn("private_key", result)
        self.assertIsNotNone(
            self.control.authenticate_device(result["device_token"])
        )

    def test_gateway_discovery_requires_device_auth(self):
        status, _ = self.request("GET", "/v1/gateways")
        self.assertEqual(status, 401)
        self.enroll()
        status, body = self.request(
            "GET", "/v1/gateways", token=self.device_token
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["gateways"], [])

    def test_activation_uses_authenticated_device_identity(self):
        self.enroll()
        code = self.control.issue_test_activation_code(24)
        status, body = self.request(
            "POST", "/v1/entitlements/activate",
            {"activation_code": code, "device_id": "forged-device"},
            self.device_token,
        )
        self.assertEqual(status, 400)

        status, body = self.request(
            "POST", "/v1/entitlements/activate",
            {"activation_code": code}, self.device_token,
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "active")

        status, body = self.request(
            "GET", "/v1/entitlements", token=self.device_token
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(body["entitlements"]), 1)

    def test_admin_rejects_non_integer_pass_durations(self):
        invalid_durations = (24.0, True, "24", 48)
        for hours in invalid_durations:
            with self.subTest(hours=hours):
                status, _ = self.request(
                    "POST",
                    "/v1/admin/activation-codes",
                    {"duration_hours": hours},
                    ADMIN,
                )
                self.assertEqual(status, 400)

    def test_admin_code_issuance_and_device_revocation(self):
        self.enroll()
        status, _ = self.request(
            "POST", "/v1/admin/activation-codes",
            {"duration_hours": 24}, self.device_token,
        )
        self.assertEqual(status, 403)

        status, result = self.request(
            "POST", "/v1/admin/activation-codes",
            {"duration_hours": 24}, ADMIN,
        )
        self.assertEqual(status, 201)
        self.assertTrue(result["activation_code"])

        status, _ = self.request(
            "POST",
            "/v1/admin/devices/" + self.device_id + "/revoke",
            {}, ADMIN,
        )
        self.assertEqual(status, 202)

        status, _ = self.request(
            "GET", "/v1/gateways", token=self.device_token
        )
        self.assertEqual(status, 401)


if __name__ == "__main__":
    unittest.main()
