import base64
import unittest
from datetime import datetime, timedelta, timezone

from entitlements import Gateway, LocalControlPlane, validate_wireguard_public_key


def public_key(seed: int) -> str:
    return base64.b64encode(bytes([seed]) * 32).decode("ascii")


class ControlPlaneRulesTests(unittest.TestCase):
    def setUp(self):
        self.cp = LocalControlPlane()
        self.now = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)
        self.device = self.cp.enroll_device(public_key(1))
        self.gateway = Gateway(
            gateway_id="gw-local-01",
            display_name="Local test gateway",
            region="local",
            endpoint="127.0.0.1:51820",
            server_public_key=public_key(2),
        )
        self.cp.register_gateway(self.gateway)

    def test_public_key_validation(self):
        self.assertTrue(validate_wireguard_public_key(public_key(3)))
        self.assertFalse(validate_wireguard_public_key("not-a-key"))
        self.assertFalse(validate_wireguard_public_key(base64.b64encode(b"short").decode()))

    def test_enrollment_rejects_duplicate_key(self):
        with self.assertRaises(ValueError):
            self.cp.enroll_device(public_key(1))

    def test_gateway_discovery_excludes_unhealthy_or_full(self):
        self.cp.register_gateway(Gateway(
            "gw-full", "Full gateway", "local", "127.0.0.1:51821",
            public_key(4), capacity_state="full"
        ))
        self.assertEqual([self.gateway.gateway_id], [g.gateway_id for g in self.cp.eligible_gateways()])

    def test_24_hour_pass_allows_tunnel_until_expiry(self):
        code = self.cp.issue_test_activation_code(24)
        entitlement = self.cp.activate_pass(code, self.device.device_id, self.now)
        allowed = self.cp.authorize_tunnel(self.device.device_id, self.gateway.gateway_id, self.now + timedelta(hours=23))
        self.assertEqual(self.gateway.gateway_id, allowed.gateway_id)
        with self.assertRaises(PermissionError):
            self.cp.authorize_tunnel(self.device.device_id, self.gateway.gateway_id, self.now + timedelta(hours=24))
        self.assertEqual("expired", entitlement.status_at(self.now + timedelta(hours=24)))

    def test_activation_code_is_one_time(self):
        code = self.cp.issue_test_activation_code(72)
        self.cp.activate_pass(code, self.device.device_id, self.now)
        with self.assertRaises(ValueError):
            self.cp.activate_pass(code, self.device.device_id, self.now)

    def test_only_supported_durations_are_issued(self):
        for hours in (1, 12, 48, 720):
            with self.assertRaises(ValueError):
                self.cp.issue_test_activation_code(hours)

    def test_revocation_blocks_tunnel_and_revokes_pass(self):
        code = self.cp.issue_test_activation_code(168)
        entitlement = self.cp.activate_pass(code, self.device.device_id, self.now)
        self.cp.revoke_device(self.device.device_id)
        self.assertEqual("revoked", entitlement.status_at(self.now + timedelta(minutes=1)))
        with self.assertRaises(PermissionError):
            self.cp.authorize_tunnel(self.device.device_id, self.gateway.gateway_id, self.now)

    def test_tunnel_requires_active_entitlement(self):
        with self.assertRaises(PermissionError):
            self.cp.authorize_tunnel(self.device.device_id, self.gateway.gateway_id, self.now)

    def test_naive_datetime_is_rejected(self):
        code = self.cp.issue_test_activation_code(24)
        with self.assertRaises(ValueError):
            self.cp.activate_pass(code, self.device.device_id, datetime(2026, 11, 26, 12, 0))


if __name__ == "__main__":
    unittest.main()
