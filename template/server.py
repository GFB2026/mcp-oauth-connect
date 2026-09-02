"""Minimal FastMCP server with OAuth 2.0 DCR.

Public ping-only example (not the paid SKU). Exposes ping only — no host shell,
no mail, no student data. The $149 SKU is a diagnose-gated four-host transcript.

Required env:
  MCP_ISSUER_URL   public HTTPS origin (no trailing slash), e.g. https://mcp.example.com
Optional:
  MCP_RESOURCE_URL MCP resource identifier (default: $MCP_ISSUER_URL/mcp)
  FASTMCP_HOST     bind host (default 127.0.0.1)
  FASTMCP_PORT     bind port (default 8000)
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

from mcp.server.auth.settings import (  # noqa: E402
    AuthSettings,
    ClientRegistrationOptions,
    RevocationOptions,
)
from mcp.server.fastmcp import FastMCP  # noqa: E402

from oauth_provider import AllowlistOAuthProvider  # noqa: E402

_issuer = os.environ.get("MCP_ISSUER_URL", "").rstrip("/")
if not _issuer:
    raise SystemExit("Set MCP_ISSUER_URL to the public HTTPS origin of this server")
_resource = os.environ.get("MCP_RESOURCE_URL", _issuer + "/mcp").rstrip("/")


def origin_prm_payload() -> dict[str, object]:
    """RFC 9728 origin document. FastMCP 1.27 only mounts the path-appended form
    when resource_server_url has a path; Anthropic also curls the origin URL.
    """
    return {
        "resource": _resource,
        "authorization_servers": [_issuer],
        "bearer_methods_supported": ["header"],
    }


mcp = FastMCP(
    "mcp-oauth-connect",
    auth_server_provider=AllowlistOAuthProvider(),
    auth=AuthSettings(
        issuer_url=_issuer,
        resource_server_url=_resource,
        client_registration_options=ClientRegistrationOptions(enabled=True),
        revocation_options=RevocationOptions(enabled=True),
    ),
    transport_security={"enable_dns_rebinding_protection": False},
)


@mcp.tool()
def ping() -> str:
    """Health check. Returns pong. No host access."""
    return "pong"


if __name__ == "__main__":
    import uvicorn
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    app = mcp.streamable_http_app()

    async def origin_prm(_request: Request) -> JSONResponse:
        return JSONResponse(origin_prm_payload())

    app.router.routes.insert(
        0,
        Route("/.well-known/oauth-protected-resource", origin_prm, methods=["GET", "OPTIONS"]),
    )

    host = os.environ.get("FASTMCP_HOST", "127.0.0.1")
    port = int(os.environ.get("FASTMCP_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
