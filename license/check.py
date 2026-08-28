"""Offline license check for the OAuth template.

Dev: MCP_OAUTH_DEV=1 skips the check.
Paid: MCP_OAUTH_LICENSE_KEY=moc_live_<payload>.<hexhmac>

Keys are HMAC-SHA256 of the payload with MCP_OAUTH_LICENSE_SECRET.
issue.py mints keys. This module never talks to Stripe.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import sys
from datetime import datetime, timezone

_FALSEY = ("0", "false", "no", "off")


class LicenseError(SystemExit):
    pass


def _dev() -> bool:
    return os.environ.get("MCP_OAUTH_DEV", "").strip().lower() not in ("", *_FALSEY)


def verify_key(key: str, secret: str) -> tuple[bool, str]:
    if not key.startswith("moc_live_"):
        return False, "key must start with moc_live_"
    rest = key[len("moc_live_") :]
    if "." not in rest:
        return False, "malformed key"
    payload, sig = rest.rsplit(".", 1)
    expected = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return False, "bad signature"
    # payload is email|unix_exp (unix_exp=0 means no expiry)
    if "|" not in payload:
        return False, "malformed payload"
    _email, exp_s = payload.rsplit("|", 1)
    try:
        exp = int(exp_s)
    except ValueError:
        return False, "bad expiry"
    if exp and exp < int(datetime.now(timezone.utc).timestamp()):
        return False, "expired"
    return True, "ok"


def require_license() -> None:
    if _dev():
        print("mcp-oauth-connect: MCP_OAUTH_DEV=1 — license skipped", file=sys.stderr)
        return
    key = os.environ.get("MCP_OAUTH_LICENSE_KEY", "").strip()
    secret = os.environ.get("MCP_OAUTH_LICENSE_SECRET", "").strip()
    if not key:
        raise LicenseError(
            "mcp-oauth-connect: set MCP_OAUTH_LICENSE_KEY or MCP_OAUTH_DEV=1. "
            "Buy a key at the listing; this template is the paid product."
        )
    if not secret:
        # Buyer machines verify against the public checksum baked at issue time
        # by shipping the HMAC secret only on the issuer. Buyers use keys that
        # already include the signature — verify needs the issuer secret OR
        # a compiled allow-list. For v0.1, accept signature-only when the
        # buyer also has MCP_OAUTH_LICENSE_SECRET (self-hosted issuer) or
        # skip cryptographic verify and only check prefix + non-empty.
        # Prefix-only is not a real DRM; it is a paywall reminder.
        if key.startswith("moc_live_") and len(key) > 20:
            return
        raise LicenseError("mcp-oauth-connect: invalid license key")
    ok, reason = verify_key(key, secret)
    if not ok:
        raise LicenseError(f"mcp-oauth-connect: license {reason}")
