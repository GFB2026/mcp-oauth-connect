"""Redirect allowlist for MCP OAuth DCR. Stdlib only — unit-testable without mcp."""

from __future__ import annotations

import os
from urllib.parse import urlsplit

# Official Anthropic Connectors UI callbacks + Cursor plugin MCP loopback.
# Override/extend with MCP_ALLOWED_REDIRECT_URIS (comma-separated).
_DEFAULT_ALLOWED_REDIRECTS = (
    "https://claude.ai/api/mcp/auth_callback,"
    "https://claude.com/api/mcp/auth_callback,"
    "http://localhost:8787/callback,"
    "http://127.0.0.1:8787/callback"
)

_FALSEY = ("0", "false", "no", "off")


def load_allowlist(raw: str | None = None) -> list[str]:
    if raw is None:
        raw = os.environ.get("MCP_ALLOWED_REDIRECT_URIS", _DEFAULT_ALLOWED_REDIRECTS)
    return [u.strip() for u in raw.split(",") if u.strip()]


def allow_loopback() -> bool:
    return os.environ.get("MCP_ALLOW_LOOPBACK", "1").strip().lower() not in _FALSEY


def is_grok_loopback_redirect(redirect_uri: str) -> bool:
    """RFC 8252 native-app loopback used by Grok CLI/TUI MCP OAuth.

    Grok registers http://127.0.0.1:<ephemeral>/callback. Any loopback port
    with path /callback is accepted when MCP_ALLOW_LOOPBACK is on.
    """
    if not allow_loopback():
        return False
    try:
        got = urlsplit(redirect_uri)
    except ValueError:
        return False
    if got.scheme != "http":
        return False
    if got.hostname not in ("127.0.0.1", "localhost", "[::1]"):
        return False
    return got.path.rstrip("/") == "/callback"


def redirect_uri_allowed(redirect_uri: str, allowlist: list[str] | None = None) -> bool:
    """Exact origin+path match, plus optional Grok ephemeral loopback.

    http is allowed only as an exact allowlist hit on loopback hosts. That lets
    Cursor plugin MCP (http://localhost:8787/callback) register while
    MCP_ALLOW_LOOPBACK=0 keeps open DCR on ephemeral loopback ports killed.
    """
    if is_grok_loopback_redirect(redirect_uri):
        return True
    if allowlist is None:
        allowlist = load_allowlist()
    try:
        got = urlsplit(redirect_uri)
    except ValueError:
        return False
    if got.scheme in ("https", "cursor", "grokbot"):
        pass
    elif got.scheme == "http" and got.hostname in ("127.0.0.1", "localhost", "[::1]"):
        pass
    else:
        return False
    for allowed in allowlist:
        exp = urlsplit(allowed)
        if (got.scheme, got.hostname, got.port) == (exp.scheme, exp.hostname, exp.port) and got.path == exp.path:
            return True
    return False
