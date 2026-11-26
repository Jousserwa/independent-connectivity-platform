"""SQLite-backed control plane for local development.

This is not yet a deployed API or production network service.
"""
from __future__ import annotations

import secrets
import sqlite3
from datetime import datetime
from typing import Optional

from entitlements import (
    ALLOWED_PASS_HOURS,
    Device,
    Gateway,
    Entitlement,
    validate_wireguard_public_key,
)
from storage import SQLiteStore


class PersistentControlPlane:
    """Persistent implementation of the control-plane rules."""

    def __init__(self, store: Optional[SQLiteStore] = None):
        self.store = store or SQLiteStore()

    def enroll_device(
        self,
        public_key: str,
        platform: str = "android",
    ) -> Device:
        if platform != "android":
            raise ValueError("unsupported platform")

        if not validate_wireguard_public_key(public_key):
            raise ValueError("invalid WireGuard public key")

        existing = self.store.get_device_by_public_key(public_key)
        if existing is not None:
            raise ValueError("public key already enrolled")

        device = Device(
            device_id="dev_" + secrets.token_urlsafe(12),
            public_key=public_key,
            platform=platform,
        )

        try:
            self.store.save_device(device)
        except sqlite3.IntegrityError as exc:
            raise ValueError("public key or device already enrolled") from exc

        return device

    def get_device(self, device_id: str):
        return self.store.get_device(device_id)

    def register_gateway(self, gateway: Gateway) -> None:
        if not gateway.gateway_id or not gateway.endpoint:
            raise ValueError("gateway id and endpoint are required")

        if gateway.status not in {
            "healthy", "degraded", "unavailable"
        }:
            raise ValueError("invalid gateway status")

        if gateway.capacity_state not in {
            "available", "limited", "full"
        }:
            raise ValueError("invalid gateway capacity state")

        if not validate_wireguard_public_key(gateway.server_public_key):
            raise ValueError("invalid gateway public key")

        self.store.save_gateway(gateway)

    def eligible_gateways(self):
        return self.store.eligible_gateways()

    def issue_test_activation_code(self, duration_hours: int) -> str:
        if duration_hours not in ALLOWED_PASS_HOURS:
            raise ValueError(
                "only 24, 72, or 168 hour test passes are allowed"
            )

        code = secrets.token_urlsafe(24)
        self.store.save_activation_code(code, duration_hours)
        return code

    def activate_pass(
        self,
        activation_code: str,
        device_id: str,
        now: Optional[datetime] = None,
    ) -> Entitlement:
        return self.store.activate_code_for_device(
            activation_code,
            device_id,
            now,
        )

    def get_entitlements(self, device_id: str):
        return self.store.get_entitlements(device_id)

    def revoke_device(self, device_id: str) -> None:
        self.store.revoke_device(device_id)
