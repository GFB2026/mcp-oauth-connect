#!/usr/bin/env python3
"""Mint a moc_live_ key. Run only on the seller machine.

  MCP_OAUTH_LICENSE_SECRET=... python license/issue.py buyer@example.com [days]

days=0 means no expiry. Does not call Stripe — paste the printed key into
the Payment Link fulfillment note until a webhook is wired.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import sys
import time


def main(argv: list[str]) -> int:
    secret = os.environ.get("MCP_OAUTH_LICENSE_SECRET", "").strip()
    if not secret:
        print("Set MCP_OAUTH_LICENSE_SECRET", file=sys.stderr)
        return 2
    if len(argv) < 2:
        print("usage: issue.py email [days]", file=sys.stderr)
        return 2
    email = argv[1].strip()
    days = int(argv[2]) if len(argv) > 2 else 365
    exp = 0 if days == 0 else int(time.time()) + days * 86400
    payload = f"{email}|{exp}"
    sig = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    print(f"moc_live_{payload}.{sig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
