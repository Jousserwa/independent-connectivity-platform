"""SQLite persistence for the Independent Connectivity Platform prototype."""
from __future__ import annotations

import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from entitlements import Device, Gateway, Entitlement


DEFAULT_DB = Path(__file__).parent / "data" / "control_plane.sqlite3"


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat()


def _datetime(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(timezone.utc)


class SQLiteStore:
    """Persistent local storage. Not yet a production database service."""

    def __init__(self, database_path=DEFAULT_DB):
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self):
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    public_key TEXT NOT NULL UNIQUE,
                    platform TEXT NOT NULL,
                    revoked INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS gateways (
                    gateway_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    region TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    server_public_key TEXT NOT NULL,
                    status TEXT NOT NULL,
                    capacity_state TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS activation_codes (
                    code_hash TEXT PRIMARY KEY,
                    duration_hours INTEGER NOT NULL,
                    redeemed INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS entitlements (
                    entitlement_id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL REFERENCES devices(device_id),
                    starts_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    revoked INTEGER NOT NULL DEFAULT 0
                );
            """)

    def save_device(self, device: Device):
        with self._connect() as db:
            db.execute(
                """INSERT INTO devices
                   (device_id, public_key, platform, revoked)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(device_id) DO UPDATE SET
                   public_key=excluded.public_key,
                   platform=excluded.platform,
                   revoked=excluded.revoked""",
                (device.device_id, device.public_key,
                 device.platform, int(device.revoked)),
            )

    def get_device(self, device_id: str) -> Optional[Device]:
        with self._connect() as db:
            row = db.execute(
                "SELECT * FROM devices WHERE device_id=?",
                (device_id,),
            ).fetchone()
        if row is None:
            return None
        return Device(row["device_id"], row["public_key"],
                      row["platform"], bool(row["revoked"]))

    def save_gateway(self, gateway: Gateway):
        with self._connect() as db:
            db.execute(
                """INSERT INTO gateways VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(gateway_id) DO UPDATE SET
                   display_name=excluded.display_name,
                   region=excluded.region,
                   endpoint=excluded.endpoint,
                   server_public_key=excluded.server_public_key,
                   status=excluded.status,
                   capacity_state=excluded.capacity_state""",
                (gateway.gateway_id, gateway.display_name, gateway.region,
                 gateway.endpoint, gateway.server_public_key,
                 gateway.status, gateway.capacity_state),
            )

    def eligible_gateways(self):
        with self._connect() as db:
            rows = db.execute(
                """SELECT * FROM gateways
                   WHERE status='healthy' AND capacity_state!='full'"""
            ).fetchall()
        return [
            Gateway(row["gateway_id"], row["display_name"], row["region"],
                    row["endpoint"], row["server_public_key"],
                    row["status"], row["capacity_state"])
            for row in rows
        ]

    def save_activation_code(self, code: str, duration_hours: int):
        if duration_hours not in {24, 72, 168}:
            raise ValueError("unsupported pass duration")
        digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
        with self._connect() as db:
            db.execute(
                "INSERT INTO activation_codes (code_hash, duration_hours) VALUES (?, ?)",
                (digest, duration_hours),
            )

    def redeem_activation_code(self, code: str) -> Optional[int]:
        digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                """SELECT duration_hours FROM activation_codes
                   WHERE code_hash=? AND redeemed=0""",
                (digest,),
            ).fetchone()
            if row is None:
                return None
            db.execute(
                "UPDATE activation_codes SET redeemed=1 WHERE code_hash=?",
                (digest,),
            )
            return int(row["duration_hours"])

    def save_entitlement(self, entitlement: Entitlement):
        with self._connect() as db:
            db.execute(
                """INSERT INTO entitlements
                   (entitlement_id, device_id, starts_at, expires_at, revoked)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(entitlement_id) DO UPDATE SET
                   starts_at=excluded.starts_at,
                   expires_at=excluded.expires_at,
                   revoked=excluded.revoked""",
                (entitlement.entitlement_id, entitlement.device_id,
                 _timestamp(entitlement.starts_at),
                 _timestamp(entitlement.expires_at),
                 int(entitlement.revoked)),
            )

    def get_entitlements(self, device_id: str):
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM entitlements WHERE device_id=?",
                (device_id,),
            ).fetchall()
        return [
            Entitlement(row["entitlement_id"], row["device_id"],
                        _datetime(row["starts_at"]),
                        _datetime(row["expires_at"]),
                        bool(row["revoked"]))
            for row in rows
        ]

    def revoke_device(self, device_id: str):
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            result = db.execute(
                "UPDATE devices SET revoked=1 WHERE device_id=?",
                (device_id,),
            )
            if result.rowcount == 0:
                raise ValueError("unknown device")
            db.execute(
                "UPDATE entitlements SET revoked=1 WHERE device_id=?",
                (device_id,),
            )
