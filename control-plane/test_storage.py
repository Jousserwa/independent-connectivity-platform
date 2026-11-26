import base64
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from storage import SQLiteStore
from entitlements import Device, Gateway, Entitlement


class SQLiteStoreTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "test.sqlite3"
        self.store = SQLiteStore(self.db_path)
        self.device = Device(
            "dev_test",
            base64.b64encode(bytes([1]) * 32).decode()
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_device_survives_store_restart(self):
        self.store.save_device(self.device)
        restarted = SQLiteStore(self.db_path)
        self.assertEqual(restarted.get_device("dev_test"), self.device)

    def test_activation_code_is_redeemed_only_once(self):
        self.store.save_activation_code("test-code", 24)
        self.assertEqual(self.store.redeem_activation_code("test-code"), 24)
        self.assertIsNone(self.store.redeem_activation_code("test-code"))

    def test_activation_code_restrictions(self):
        with self.assertRaises(ValueError):
            self.store.save_activation_code("bad-code", 48)

    def test_gateway_filtering(self):
        key = base64.b64encode(bytes([2]) * 32).decode()
        good = Gateway(
            "gw_good", "Test Gateway", "Uganda",
            "198.51.100.10:51820", key
        )
        full = Gateway(
            "gw_full", "Full Gateway", "Uganda",
            "198.51.100.11:51820", key,
            capacity_state="full"
        )
        self.store.save_gateway(good)
        self.store.save_gateway(full)
        self.assertEqual(
            [g.gateway_id for g in self.store.eligible_gateways()],
            ["gw_good"]
        )

    def test_entitlement_survives_restart(self):
        self.store.save_device(self.device)
        start = datetime.now(timezone.utc)
        entitlement = Entitlement(
            "ent_test", "dev_test",
            start, start + timedelta(hours=24)
        )
        self.store.save_entitlement(entitlement)
        restarted = SQLiteStore(self.db_path)
        saved = restarted.get_entitlements("dev_test")
        self.assertEqual(saved, [entitlement])

    def test_revocation_persists(self):
        self.store.save_device(self.device)
        start = datetime.now(timezone.utc)
        self.store.save_entitlement(Entitlement(
            "ent_revoke", "dev_test",
            start, start + timedelta(hours=24)
        ))
        self.store.revoke_device("dev_test")
        restarted = SQLiteStore(self.db_path)
        self.assertTrue(restarted.get_device("dev_test").revoked)
        self.assertTrue(restarted.get_entitlements("dev_test")[0].revoked)


if __name__ == "__main__":
    unittest.main()
