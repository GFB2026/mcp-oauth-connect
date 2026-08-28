#!/usr/bin/env python3
"""Probe an MCP HTTPS URL for OAuth 2.0 / DCR that Connectors UIs actually need.

Stdlib only. Exit 0 if the connector-critical checks pass; 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urljoin, urlparse

REQUIRED_AS_KEYS = ("issuer", "authorization_endpoint", "token_endpoint", "registration_endpoint")


def _get(url: str, timeout: float = 12.0) -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "mcp-oauth-connect/0.1"})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, {k.lower(): v for k, v in resp.headers.items()}, resp.read()
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        return e.code, {k.lower(): v for k, v in e.headers.items()}, body


def diagnose(base: str) -> dict[str, Any]:
    origin = base.rstrip("/")
    parsed = urlparse(origin)
    if parsed.scheme != "https":
        return {
            "ok": False,
            "error": "URL must be https (Connectors UI will not complete OAuth over http)",
            "url": origin,
        }
    as_url = urljoin(origin + "/", ".well-known/oauth-authorization-server")
    mcp_url = origin if origin.endswith("/mcp") else origin + "/mcp"
    report: dict[str, Any] = {"url": origin, "as_url": as_url, "mcp_url": mcp_url, "checks": {}, "ok": True}

    status, headers, body = _get(as_url)
    as_ok = False
    as_json: dict[str, Any] = {}
    try:
        as_json = json.loads(body.decode("utf-8", errors="replace")) if body else {}
    except json.JSONDecodeError:
        as_json = {}
    missing = [k for k in REQUIRED_AS_KEYS if not as_json.get(k)]
    as_ok = status == 200 and not missing
    report["checks"]["authorization_server_metadata"] = {
        "ok": as_ok,
        "status": status,
        "missing": missing,
        "issuer": as_json.get("issuer"),
        "registration_endpoint": as_json.get("registration_endpoint"),
    }
    if not as_ok:
        report["ok"] = False

    status, headers, _body = _get(mcp_url)
    www = headers.get("www-authenticate", "")
    has_resource = "resource_metadata=" in www.lower()
    # Unauthenticated MCP must 401 with WWW-Authenticate Bearer ... resource_metadata=
    mcp_ok = status == 401 and "bearer" in www.lower() and has_resource
    report["checks"]["unauthenticated_mcp"] = {
        "ok": mcp_ok,
        "status": status,
        "www_authenticate": www[:300],
        "hint": None
        if mcp_ok
        else "Need HTTP 401 plus WWW-Authenticate: Bearer ... resource_metadata=<url>. Static Authorization middleware will curl-pass and fail in Connectors UI.",
    }
    if not mcp_ok:
        report["ok"] = False

    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Diagnose MCP OAuth for claude.ai / Cursor / Grok")
    p.add_argument("url", help="Public HTTPS origin or /mcp URL")
    args = p.parse_args(argv)
    report = diagnose(args.url)
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
