"""Local-first HTTP API for the Independent Connectivity Platform."""
from __future__ import annotations

import hmac
import json
import os
import re
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from entitlements import Gateway
from persistent import PersistentControlPlane


class RequestError(ValueError):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def _token_matches(provided, expected):
    if not isinstance(provided, str):
        return False
    return hmac.compare_digest(
        provided.encode("utf-8"),
        expected.encode("utf-8"),
    )


MAX_BODY = 16_384


def _entitlement_json(item):
    now = datetime.now(timezone.utc)
    return {
        "entitlement_id": item.entitlement_id,
        "status": item.status_at(now),
        "starts_at": item.starts_at.isoformat(),
        "expires_at": item.expires_at.isoformat(),
    }


def make_server(host, port, control, enrollment_token, admin_token):
    if not enrollment_token or not admin_token:
        raise ValueError("enrollment and admin tokens are required")

    class Handler(BaseHTTPRequestHandler):
        server_version = "ICP-ControlPlane/0.1"

        def log_message(self, fmt, *args):
            # Avoid logging authorization headers or request secrets.
            return

        def send_error(self, code, message=None, explain=None):
            status = 405 if code == 501 else code
            labels = {
                400: "bad request",
                401: "unauthorized",
                403: "forbidden",
                404: "not found",
                405: "method not allowed",
                411: "length required",
                413: "payload too large",
                414: "URI too long",
                415: "unsupported media type",
                431: "request headers too large",
            }
            self.close_connection = True
            body = json.dumps({
                "error": labels.get(status, "HTTP request error")
            }).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            if status == 405:
                self.send_header("Allow", "GET, POST")
            self.end_headers()
            self.wfile.write(body)

        def reply(self, status, payload):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def fail(self, status, message):
            self.reply(status, {"error": message})

        def bearer(self):
            value = self.headers.get("Authorization", "")
            if not value.startswith("Bearer "):
                return None
            return value[7:].strip() or None

        def require_device(self):
            token = self.bearer()
            device = control.authenticate_device(token) if token else None
            if device is None:
                self.fail(401, "device authentication required")
                return None
            return device

        def require_admin(self):
            if not _token_matches(self.bearer(), admin_token):
                self.fail(403, "admin permission required")
                return False
            return True

        def read_json(self):
            if self.headers.get_all("Transfer-Encoding"):
                self.close_connection = True
                raise RequestError(400, "Transfer-Encoding is not supported")

            lengths = self.headers.get_all("Content-Length", [])
            if len(lengths) > 1:
                self.close_connection = True
                raise RequestError(400, "duplicate Content-Length")

            if not lengths:
                self.close_connection = True
                raise RequestError(411, "Content-Length is required")

            raw_length = lengths[0]
            if not raw_length.isascii() or not raw_length.isdecimal():
                self.close_connection = True
                raise RequestError(400, "invalid Content-Length")

            length = int(raw_length)
            if length > MAX_BODY:
                self.close_connection = True
                raise RequestError(413, "request body exceeds the size limit")
            if length < 1:
                self.close_connection = True
                raise RequestError(400, "request body is empty")

            if self.headers.get_content_type() != "application/json":
                self.close_connection = True
                raise RequestError(415, "Content-Type must be application/json")

            raw = self.rfile.read(length)
            if len(raw) != length:
                self.close_connection = True
                raise RequestError(400, "request body is incomplete")

            def reject_duplicate_keys(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise RequestError(400, "duplicate JSON object key")
                    result[key] = value
                return result

            try:
                value = json.loads(
                    raw.decode("utf-8"),
                    object_pairs_hook=reject_duplicate_keys,
                )
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise ValueError("invalid JSON body")

            if not isinstance(value, dict):
                raise ValueError("JSON body must be an object")
            return value

        def do_GET(self):
            try:
                self._handle_get()
            except Exception:
                # Never expose internal exception details to API clients.
                self.fail(500, "internal server error")

        def _handle_get(self):
            path = self.path.split("?", 1)[0]

            if path == "/v1/health":
                return self.reply(200, {"status": "ok"})

            if path == "/v1/gateways":
                device = self.require_device()
                if device is None:
                    return
                gateways = control.eligible_gateways()
                return self.reply(200, {
                    "gateways": [
                        {
                            "gateway_id": g.gateway_id,
                            "display_name": g.display_name,
                            "region": g.region,
                            "status": g.status,
                            "endpoint": g.endpoint,
                            "capacity_state": g.capacity_state,
                        }
                        for g in gateways
                    ]
                })

            if path == "/v1/entitlements":
                device = self.require_device()
                if device is None:
                    return
                items = control.get_entitlements(device.device_id)
                return self.reply(200, {
                    "entitlements": [_entitlement_json(x) for x in items]
                })

            return self.fail(404, "route not found")

        def do_POST(self):
            path = self.path.split("?", 1)[0]

            try:
                if path == "/v1/devices/enroll":
                    if not _token_matches(self.bearer(), enrollment_token):
                        return self.fail(401, "invalid enrollment token")
                    data = self.read_json()
                    if set(data) - {"device_public_key", "platform", "app_version"}:
                        raise ValueError("unexpected request fields")
                    if not isinstance(data.get("device_public_key"), str):
                        raise ValueError("device_public_key is required")
                    if data.get("platform") != "android":
                        raise ValueError("platform must be android")

                    device, raw_token = control.enroll_device_with_token(
                        data["device_public_key"], data["platform"]
                    )
                    return self.reply(201, {
                        "device_id": device.device_id,
                        "device_token": raw_token,
                        "status": "enrolled",
                    })

                if path == "/v1/entitlements/activate":
                    device = self.require_device()
                    if device is None:
                        return
                    data = self.read_json()
                    if set(data) != {"activation_code"}:
                        raise ValueError(
                            "only activation_code is accepted; device identity comes from authentication"
                        )
                    if not isinstance(data["activation_code"], str):
                        raise ValueError("activation_code must be a string")
                    item = control.activate_pass(
                        data["activation_code"], device.device_id
                    )
                    return self.reply(200, _entitlement_json(item))

                if path == "/v1/admin/activation-codes":
                    if not self.require_admin():
                        return
                    data = self.read_json()
                    if set(data) != {"duration_hours"}:
                        raise ValueError("duration_hours is required")
                    if type(data["duration_hours"]) is not int:
                        raise ValueError("duration_hours must be an integer")
                    code = control.issue_test_activation_code(
                        data["duration_hours"]
                    )
                    return self.reply(201, {
                        "activation_code": code,
                        "duration_hours": data["duration_hours"],
                    })

                if path == "/v1/admin/gateways":
                    if not self.require_admin():
                        return
                    data = self.read_json()
                    required = {
                        "gateway_id", "display_name", "region", "endpoint",
                        "server_public_key", "status", "capacity_state",
                    }
                    if set(data) != required:
                        raise ValueError("gateway fields are missing or unexpected")
                    gateway = Gateway(**data)
                    control.register_gateway(gateway)
                    return self.reply(201, {"gateway_id": gateway.gateway_id})

                match = re.fullmatch(
                    r"/v1/admin/devices/([^/]+)/revoke", path
                )
                if match:
                    if not self.require_admin():
                        return
                    control.revoke_device(match.group(1))
                    return self.reply(202, {"status": "revoked"})

                return self.fail(404, "route not found")

            except RequestError as exc:
                return self.fail(exc.status, str(exc))
            except ValueError as exc:
                return self.fail(400, str(exc))
            except Exception:
                # Never return internal exceptions, database details, or secrets.
                return self.fail(500, "internal server error")

    return ThreadingHTTPServer((host, port), Handler)


def main():
    enrollment = os.environ.get("ICP_ENROLLMENT_TOKEN")
    admin = os.environ.get("ICP_ADMIN_TOKEN")
    if not enrollment or not admin:
        raise SystemExit(
            "Set ICP_ENROLLMENT_TOKEN and ICP_ADMIN_TOKEN before starting."
        )

    server = make_server(
        "127.0.0.1", 8765, PersistentControlPlane(),
        enrollment, admin
    )
    print("ICP local API listening on http://127.0.0.1:8765")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local API.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
