"""SQLite-backed control plane for local development.

This is not yet a deployed API or production network service.
"""
from __future__ import annotations

import secrets
import hashlib
import sqlite3
import ipaddress
import re
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


def _valid_gateway_endpoint(endpoint: str) -> bool:
    """Validate a WireGuard host:port endpoint without accepting URLs."""
    if not isinstance(endpoint, str) or not endpoint or len(endpoint) > 300:
        return False

    if endpoint.startswith("["):
        closing = endpoint.find("]")
        if closing < 0 or endpoint[closing + 1:closing + 2] != ":":
            return False
        host = endpoint[1:closing]
        port = endpoint[closing + 2:]
        try:
            if ipaddress.ip_address(host).version != 6:
                return False
        except ValueError:
            return False
    else:
        if endpoint.count(":") != 1:
            return False
        host, port = endpoint.rsplit(":", 1)

        if not host:
            return False

        try:
            ipaddress.ip_address(host)
        except ValueError:
            # Do not accept malformed dotted IPv4 addresses as DNS names.
            if re.fullmatch(r"[0-9]+(?:\.[0-9]+){3}", host):
                return False
            if len(host) > 253:
                return False
            labels = host.split(".")
            if not all(
                1 <= len(label) <= 63
                and re.fullmatch(
                    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?",
                    label,
                )
                for label in labels
            ):
                return False

    return (
        bool(port)
        and port.isascii()
        and port.isdecimal()
        and 1 <= int(port) <= 65535
    )


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

    def enroll_device_with_token(
        self,
        public_key: str,
        platform: str = "android",
    ) -> tuple[Device, str]:
        if platform != "android":
            raise ValueError("unsupported platform")
        if not validate_wireguard_public_key(public_key):
            raise ValueError("invalid WireGuard public key")
        if self.store.get_device_by_public_key(public_key) is not None:
            raise ValueError("public key already enrolled")

        device = Device(
            device_id="dev_" + secrets.token_urlsafe(12),
            public_key=public_key,
            platform=platform,
        )
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        try:
            self.store.save_device_with_token(device, token_hash)
        except sqlite3.IntegrityError as exc:
            raise ValueError("public key or device already enrolled") from exc

        return device, raw_token

    def authenticate_device(self, raw_token: str) -> Optional[Device]:
        if not isinstance(raw_token, str) or not raw_token:
            return None
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        return self.store.get_device_for_token_hash(token_hash)

    def get_device(self, device_id: str):
        return self.store.get_device(device_id)

    def register_gateway(self, gateway: Gateway) -> None:
        if not isinstance(gateway, Gateway):
            raise ValueError("gateway must be a Gateway record")

        if not isinstance(gateway.gateway_id, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", gateway.gateway_id
        ):
            raise ValueError("invalid gateway id")

        if (
            not isinstance(gateway.display_name, str)
            or not gateway.display_name.strip()
            or len(gateway.display_name) > 100
        ):
            raise ValueError("invalid gateway display name")

        if (
            not isinstance(gateway.region, str)
            or not gateway.region.strip()
            or len(gateway.region) > 80
        ):
            raise ValueError("invalid gateway region")

        if not _valid_gateway_endpoint(gateway.endpoint):
            raise ValueError("invalid gateway endpoint")

        if not isinstance(gateway.status, str) or gateway.status not in {
            "healthy", "degraded", "unavailable"
        }:
            raise ValueError("invalid gateway status")

        if (
            not isinstance(gateway.capacity_state, str)
            or gateway.capacity_state not in {
                "available", "limited", "full"
            }
        ):
            raise ValueError("invalid gateway capacity state")

        if (
            not isinstance(gateway.server_public_key, str)
            or not validate_wireguard_public_key(gateway.server_public_key)
        ):
            raise ValueError("invalid gateway public key")

        self.store.save_gateway(gateway)

    def eligible_gateways(self):
        return self.store.eligible_gateways()

    def issue_test_activation_code(self, duration_hours: int) -> str:
        if type(duration_hours) is not int or duration_hours not in ALLOWED_PASS_HOURS:
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
