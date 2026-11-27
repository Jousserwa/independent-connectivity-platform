import base64
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from entitlements import Gateway
from storage import SQLiteStore
from persistent import PersistentControlPlane


def make_key(number):
    return base64.b64encode(bytes([number]) * 32).decode()


class PersistentControlPlaneTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "persistent.sqlite3"
        self.store = SQLiteStore(self.db_path)
        self.control = PersistentControlPlane(self.store)

    def tearDown(self):
        self.temp.cleanup()

    def restart(self):
        return PersistentControlPlane(SQLiteStore(self.db_path))

    def test_device_token_authentication_survives_restart(self):
        device, token = self.control.enroll_device_with_token(make_key(11))
        restarted = self.restart()
        self.assertEqual(restarted.authenticate_device(token), device)

    def test_unknown_device_token_is_rejected(self):
        self.assertIsNone(
            self.control.authenticate_device("unknown-token")
        )

    def test_device_revocation_invalidates_token(self):
        device, token = self.control.enroll_device_with_token(make_key(12))
        self.control.revoke_device(device.device_id)
        self.assertIsNone(self.control.authenticate_device(token))

    def test_token_enrollment_rejects_duplicate_public_key(self):
        self.control.enroll_device_with_token(make_key(13))
        with self.assertRaises(ValueError):
            self.control.enroll_device_with_token(make_key(13))

    def test_device_enrollment_survives_restart(self):
        device = self.control.enroll_device(make_key(1))
        restarted = self.restart()
        self.assertEqual(restarted.get_device(device.device_id), device)

    def test_duplicate_public_key_rejected_after_restart(self):
        self.control.enroll_device(make_key(2))
        restarted = self.restart()
        with self.assertRaises(ValueError):
            restarted.enroll_device(make_key(2))

    def test_revoked_public_key_cannot_be_reenrolled(self):
        device = self.control.enroll_device(make_key(3))
        self.control.revoke_device(device.device_id)
        restarted = self.restart()
        with self.assertRaises(ValueError):
            restarted.enroll_device(make_key(3))

    def test_invalid_platform_and_public_key_rejected(self):
        with self.assertRaises(ValueError):
            self.control.enroll_device(make_key(4), "windows")
        with self.assertRaises(ValueError):
            self.control.enroll_device("not-a-valid-key")

    def test_gateway_discovery_survives_restart_and_filters(self):
        key = make_key(5)
        good = Gateway(
            "gw_good", "Good Gateway", "Uganda",
            "198.51.100.10:51820", key
        )
        full = Gateway(
            "gw_full", "Full Gateway", "Uganda",
            "198.51.100.11:51820", key,
            capacity_state="full"
        )
        unhealthy = Gateway(
            "gw_down", "Down Gateway", "Uganda",
            "198.51.100.12:51820", key,
            status="unavailable"
        )

        self.control.register_gateway(good)
        self.control.register_gateway(full)
        self.control.register_gateway(unhealthy)

        restarted = self.restart()
        found = restarted.eligible_gateways()
        self.assertEqual([g.gateway_id for g in found], ["gw_good"])

    def test_gateway_accepts_valid_endpoint_formats(self):
        key = make_key(21)
        endpoints = (
            "127.0.0.1:51820",
            "gateway.example.com:51820",
            "localhost:51820",
            "[2001:db8::1]:51820",
        )
        for index, endpoint in enumerate(endpoints):
            with self.subTest(endpoint=endpoint):
                self.control.register_gateway(Gateway(
                    f"gw_endpoint_{index}", "Test Gateway", "Uganda",
                    endpoint, key
                ))

    def test_gateway_rejects_invalid_endpoints(self):
        key = make_key(22)
        endpoints = (
            "",
            "gateway.example.com",
            "https://gateway.example.com:51820",
            "gateway.example.com/path:51820",
            "gateway.example.com:0",
            "gateway.example.com:65536",
            "gateway.example.com:abc",
            "gateway.example.com:51820:extra",
            "2001:db8::1:51820",
            "[2001:db8::1:51820",
            "[127.0.0.1]:51820",
            "bad host:51820",
        )
        for index, endpoint in enumerate(endpoints):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    self.control.register_gateway(Gateway(
                        f"gw_invalid_{index}", "Test Gateway", "Uganda",
                        endpoint, key
                    ))

    def test_gateway_rejects_invalid_metadata(self):
        key = make_key(23)
        invalid_records = (
            Gateway("bad id!", "Gateway", "Uganda",
                    "127.0.0.1:51820", key),
            Gateway("gw_name", "   ", "Uganda",
                    "127.0.0.1:51820", key),
            Gateway("gw_region", "Gateway", "",
                    "127.0.0.1:51820", key),
            Gateway("gw_long", "x" * 101, "Uganda",
                    "127.0.0.1:51820", key),
            Gateway("gw_status_type", "Gateway", "Uganda",
                    "127.0.0.1:51820", key, status=["healthy"]),
            Gateway("gw_capacity_type", "Gateway", "Uganda",
                    "127.0.0.1:51820", key, capacity_state={"state": "full"}),
            Gateway("gw_bad_ipv4", "Gateway", "Uganda",
                    "999.999.999.999:51820", key),
        )
        for gateway in invalid_records:
            with self.subTest(gateway_id=gateway.gateway_id):
                with self.assertRaises(ValueError):
                    self.control.register_gateway(gateway)

    def test_gateway_identity_cannot_be_silently_replaced(self):
        key = make_key(24)
        original = Gateway(
            "gw_immutable", "Original Gateway", "Uganda",
            "198.51.100.20:51820", key
        )
        self.control.register_gateway(original)

        changed_endpoint = Gateway(
            "gw_immutable", "Original Gateway", "Uganda",
            "198.51.100.21:51820", key
        )
        with self.assertRaises(ValueError):
            self.control.register_gateway(changed_endpoint)

        changed_key = Gateway(
            "gw_immutable", "Original Gateway", "Uganda",
            "198.51.100.20:51820", make_key(25)
        )
        with self.assertRaises(ValueError):
            self.control.register_gateway(changed_key)

        saved = self.control.eligible_gateways()
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].endpoint, original.endpoint)
        self.assertEqual(saved[0].server_public_key, original.server_public_key)

    def test_gateway_metadata_and_health_can_be_updated(self):
        key = make_key(26)
        original = Gateway(
            "gw_update", "Original Name", "Uganda",
            "198.51.100.30:51820", key
        )
        self.control.register_gateway(original)

        updated = Gateway(
            "gw_update", "Updated Name", "Central Uganda",
            "198.51.100.30:51820", key,
            status="degraded", capacity_state="limited"
        )
        self.control.register_gateway(updated)

        self.assertEqual(self.control.eligible_gateways(), [])

        restored = Gateway(
            "gw_update", "Updated Name", "Central Uganda",
            "198.51.100.30:51820", key,
            status="healthy", capacity_state="available"
        )
        self.control.register_gateway(restored)
        found = self.control.eligible_gateways()
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].display_name, "Updated Name")

    def test_only_supported_pass_durations_are_issued(self):
        for hours in (24, 72, 168):
            self.control.issue_test_activation_code(hours)

        for hours in (1, 48, 96, 240, 24.0, True, "24"):
            with self.assertRaises(ValueError):
                self.control.issue_test_activation_code(hours)

    def test_activation_survives_restart_with_correct_expiry(self):
        device = self.control.enroll_device(make_key(6))
        code = self.control.issue_test_activation_code(72)
        start = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)

        entitlement = self.control.activate_pass(
            code, device.device_id, start
        )

        restarted = self.restart()
        saved = restarted.get_entitlements(device.device_id)

        self.assertEqual(saved, [entitlement])
        self.assertEqual(
            entitlement.expires_at - entitlement.starts_at,
            timedelta(hours=72)
        )

    def test_activation_code_cannot_be_redeemed_twice(self):
        device = self.control.enroll_device(make_key(7))
        code = self.control.issue_test_activation_code(24)

        self.control.activate_pass(code, device.device_id)

        with self.assertRaises(ValueError):
            self.control.activate_pass(code, device.device_id)

        self.assertEqual(
            len(self.control.get_entitlements(device.device_id)), 1
        )

    def test_revoked_device_cannot_activate_pass(self):
        device = self.control.enroll_device(make_key(8))
        self.control.revoke_device(device.device_id)
        code = self.control.issue_test_activation_code(24)

        with self.assertRaises(ValueError):
            self.control.activate_pass(code, device.device_id)

    def test_revocation_survives_restart_and_revokes_entitlements(self):
        device = self.control.enroll_device(make_key(9))
        code = self.control.issue_test_activation_code(24)
        self.control.activate_pass(code, device.device_id)

        self.control.revoke_device(device.device_id)

        restarted = self.restart()
        saved_device = restarted.get_device(device.device_id)
        saved_entitlements = restarted.get_entitlements(device.device_id)

        self.assertTrue(saved_device.revoked)
        self.assertEqual(len(saved_entitlements), 1)
        self.assertTrue(saved_entitlements[0].revoked)


if __name__ == "__main__":
    unittest.main()
