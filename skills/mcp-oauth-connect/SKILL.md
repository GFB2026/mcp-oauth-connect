---
name: mcp-oauth-connect
description: Diagnose and fix MCP OAuth 2.0 so claude.ai Connectors, Claude Desktop, Cursor, and Grok can actually attach. Use when a connector passes curl but fails in the UI, Desktop strips url JSON, Cursor mcp.json has a static bearer, DCR / WWW-Authenticate is missing, or the user runs /mcp-oauth-connect.
---

# MCP OAuth that Connectors UIs accept

Static `Authorization: Bearer` middleware will pass curl and fail in claude.ai / Desktop / Cursor Connectors. Those hosts need MCP OAuth 2.0 with RFC 7591 dynamic client registration.

## Diagnose first

```bash
python skills/mcp-oauth-connect/scripts/diagnose.py https://mcp.example.com
```

Need all of:

1. `GET /.well-known/oauth-authorization-server` → JSON with `issuer`, `authorization_endpoint`, `token_endpoint`, `registration_endpoint`
2. Unauthenticated `GET /mcp` → **401** with `WWW-Authenticate: Bearer ... resource_metadata=...`
3. User pastes **only the URL** in the Connectors UI — no token, no client_id

## Fix (paid template)

Copy `template/` from this repo. FastMCP constructor, not middleware:

```python
FastMCP(
    "my-server",
    auth_server_provider=AllowlistOAuthProvider(),
    auth=AuthSettings(
        issuer_url=public_https_origin,
        resource_server_url=public_https_origin,
        client_registration_options=ClientRegistrationOptions(enabled=True),
    ),
)
```

Do not wrap `streamable_http_app()` with custom bearer middleware.

`issuer_url` and `resource_server_url` must both be the public HTTPS origin.

Allowlist redirect URIs (`MCP_ALLOWED_REDIRECT_URIS`):

- `https://claude.ai/api/mcp/auth_callback`
- `https://claude.com/api/mcp/auth_callback`
- Cursor plugin MCP: `http://localhost:8787/callback` (exact origin+path)
- Grok CLI/TUI: `http://127.0.0.1:<port>/callback` (ephemeral port; `MCP_ALLOW_LOOPBACK=1`)

Public clients (`token_endpoint_auth_method=none` + PKCE) must **not** get a client secret or token exchange 401s.

## Host-specific traps

- **Claude Desktop** JSON only loads stdio `command` entries. A `url` field is stripped. Use Connectors UI (Type Web, Custom). Keep `mcpServers: {}` in the JSON file.
- **Cursor** `mcp.json`: `{ "mcpServers": { "name": { "url": "https://..." } } }` — no `headers`, no static bearer.
- **Grok**: loopback `/callback` only (not `/oauth/callback`). Pin `MCP_ALLOW_LOOPBACK=0` if Grok is not a client.

## Never

- Do not put a fleet `run_command` / mail / student plane on a public template server.
- Do not list this plugin as paid on Cursor official Marketplace (terms forbid charging through that listing). Charge via Stripe / license for `template/`.
