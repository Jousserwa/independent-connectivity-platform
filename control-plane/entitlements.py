"""Local prototype domain logic.

This module has no network listener, database, or production credentials.
It is intentionally dependency-free so it can be exercised in a phone-based
Python environment such as Termux. It is not a production control plane.
"""
from __future__ import annotations

import base64
import binascii
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional


ALLOWED_PASS_HOURS = {24, 72, 168}


def _utc(value: Optional[datetime] = None) -> datetime:
    value = value or datetime.now(timezone.utc)
    if value.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def validate_wireguard_public_key(value: str) -> bool:
    """Accept a standard base64-encoded 32-byte WireGuard public key."""
    if not isinstance(value, str):
        return False
    try:
        raw = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError):
        return False
    return len(raw) == 32


@dataclass(frozen=True)
class Device:
    device_id: str
    public_key: str
    platform: str = "android"
    revoked: bool = False


@dataclass(frozen=True)
class Gateway:
    gateway_id: str
    display_name: str
    region: str
    endpoint: str
    server_public_key: str
    status: str = "healthy"
    capacity_state: str = "available"


@dataclass
class Entitlement:
    entitlement_id: str
    device_id: str
    starts_at: datetime
    expires_at: datetime
    revoked: bool = False

    def status_at(self, now: Optional[datetime] = None) -> str:
        instant = _utc(now)
        if self.revoked:
            return "revoked"
        if instant < self.starts_at:
            return "pending"
        if instant >= self.expires_at:
            return "expired"
        return "active"


class LocalControlPlane:
    """In-memory rules engine for local development and unit tests."""

    def __init__(self) -> None:
        self.devices: Dict[str, Device] = {}
        self.gateways: Dict[str, Gateway] = {}
        self.entitlements: Dict[str, Entitlement] = {}
        self.activation_codes: Dict[str, int] = {}

    def enroll_device(self, public_key: str, platform: str = "android") -> Device:
        if platform != "android":
            raise ValueError("unsupported platform")
        if not validate_wireguard_public_key(public_key):
            raise ValueError("invalid WireGuard public key")
        if any(d.public_key == public_key for d in self.devices.values()):
            raise ValueError("public key already enrolled")
        device = Device(
            device_id="dev_" + secrets.token_urlsafe(12),
            public_key=public_key,
            platform=platform,
        )
        self.devices[device.device_id] = device
        return device

    def register_gateway(self, gateway: Gateway) -> None:
        if not gateway.gateway_id or not gateway.endpoint:
            raise ValueError("gateway id and endpoint are required")
        if gateway.status not in {"healthy", "degraded", "unavailable"}:
            raise ValueError("invalid gateway status")
        if gateway.capacity_state not in {"available", "limited", "full"}:
            raise ValueError("invalid gateway capacity state")
        if not validate_wireguard_public_key(gateway.server_public_key):
            raise ValueError("invalid gateway public key")
        self.gateways[gateway.gateway_id] = gateway

    def eligible_gateways(self):
        return [
            g for g in self.gateways.values()
            if g.status == "healthy" and g.capacity_state != "full"
        ]

    def issue_test_activation_code(self, duration_hours: int) -> str:
        if type(duration_hours) is not int or duration_hours not in ALLOWED_PASS_HOURS:
            raise ValueError("only 24, 72, or 168 hour test passes are allowed")
        code = secrets.token_urlsafe(24)
        self.activation_codes[code] = duration_hours
        return code

    def activate_pass(
        self,
        activation_code: str,
        device_id: str,
        now: Optional[datetime] = None,
    ) -> Entitlement:
        device = self.devices.get(device_id)
        if device is None or device.revoked:
            raise ValueError("device is not eligible")
        duration = self.activation_codes.pop(activation_code, None)
        if duration is None:
            raise ValueError("activation code is invalid or already redeemed")
        starts = _utc(now)
        entitlement = Entitlement(
            entitlement_id="ent_" + secrets.token_urlsafe(12),
            device_id=device_id,
            starts_at=starts,
            expires_at=starts + timedelta(hours=duration),
        )
        self.entitlements[entitlement.entitlement_id] = entitlement
        return entitlement

    def revoke_device(self, device_id: str) -> None:
        device = self.devices.get(device_id)
        if device is None:
            raise ValueError("unknown device")
        self.devices[device_id] = Device(
            device_id=device.device_id,
            public_key=device.public_key,
            platform=device.platform,
            revoked=True,
        )
        for entitlement in self.entitlements.values():
            if entitlement.device_id == device_id:
                entitlement.revoked = True

    def authorize_tunnel(self, device_id: str, gateway_id: str, now=None) -> Gateway:
        device = self.devices.get(device_id)
        if device is None or device.revoked:
            raise PermissionError("device is not authorized")
        gateway = self.gateways.get(gateway_id)
        if gateway is None or gateway not in self.eligible_gateways():
            raise PermissionError("gateway is not eligible")
        active = any(
            ent.device_id == device_id and ent.status_at(now) == "active"
            for ent in self.entitlements.values()
        )
        if not active:
            raise PermissionError("no active entitlement")
        return gateway
