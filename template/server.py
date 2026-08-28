"""Minimal FastMCP server with OAuth 2.0 DCR.

This is the paid template. It exposes ping only — no host shell, no mail,
no student data. Wire your own tools below the ping definition.

Required env:
  MCP_ISSUER_URL   public HTTPS origin (no trailing slash), e.g. https://mcp.example.com
Optional:
  MCP_OAUTH_DEV=1  skip license check while developing
  MCP_OAUTH_LICENSE_KEY  paid key (see ../license/README.md)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_REPO = _ROOT.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from license.check import require_license  # noqa: E402

require_license()

from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions  # noqa: E402
from mcp.server.fastmcp import FastMCP  # noqa: E402

from oauth_provider import AllowlistOAuthProvider  # noqa: E402

_issuer = os.environ.get("MCP_ISSUER_URL", "").rstrip("/")
if not _issuer:
    raise SystemExit("Set MCP_ISSUER_URL to the public HTTPS origin of this server")

mcp = FastMCP(
    "mcp-oauth-connect",
    auth_server_provider=AllowlistOAuthProvider(),
    auth=AuthSettings(
        issuer_url=_issuer,
        resource_server_url=_issuer,
        client_registration_options=ClientRegistrationOptions(enabled=True),
    ),
    transport_security={"enable_dns_rebinding_protection": False},
)


@mcp.tool()
def ping() -> str:
    """Health check. Returns pong. No host access."""
    return "pong"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
