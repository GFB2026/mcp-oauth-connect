---
name: mcp-oauth-connect
description: Diagnose MCP OAuth 2.0 so claude.ai Connectors, Claude Desktop, Cursor, and Grok can actually attach. Use when a connector passes curl but fails in the UI, Desktop strips url JSON, Cursor mcp.json has a static bearer, DCR / WWW-Authenticate is missing, or the user runs /mcp-oauth-connect.
---

# MCP OAuth that Connectors UIs accept

Static `Authorization: Bearer` middleware will pass curl and fail in claude.ai / Desktop / Cursor Connectors. Those hosts need MCP OAuth 2.0 with RFC 7591 dynamic client registration.

This Marketplace skill is **diagnose plus host traps**. It does not sell a template.

## Diagnose first

```bash
python skills/mcp-oauth-connect/scripts/diagnose.py https://mcp.example.com
```

Need all of:

1. `GET /.well-known/oauth-authorization-server` → JSON with `issuer`, `authorization_endpoint`, `token_endpoint`, `registration_endpoint`, and `"code_challenge_methods_supported": ["S256"]`
2. RFC 9728 protected-resource metadata at `/.well-known/oauth-protected-resource` **and/or** the path-appended form `/.well-known/oauth-protected-resource/mcp` (200 JSON)
3. Unauthenticated `GET /mcp` → **401** or **405** (405 is fine; Streamable HTTP is POST)
4. Unauthenticated `POST /mcp` → **401** with `WWW-Authenticate: Bearer ... resource_metadata=<absolute https url>`
5. No cross-host `3xx` on the MCP path (Authorization is dropped)
6. User pastes **only the URL** in the Connectors UI — no token, no client_id

Relative `resource_metadata` URLs silently kill Claude Code. The probe flags them.

## Host-specific traps

- **Claude Desktop** JSON only loads stdio `command` entries. A `url` field is stripped. Use Connectors UI (Type Web, Custom). Keep `mcpServers: {}` in the JSON file.
- **Cursor** `mcp.json`: `{ "mcpServers": { "name": { "url": "https://..." } } }` — no `headers`, no static bearer.
- **Grok**: loopback `/callback` only (not `/oauth/callback`). Public clients (`token_endpoint_auth_method=none` + PKCE) must not be issued a client secret or token exchange 401s.

## Constructor (not middleware)

Use FastMCP `auth_server_provider=` + `auth=AuthSettings(...)`. Do not wrap `streamable_http_app()` with custom bearer middleware. `issuer_url` and `resource_server_url` must both be the public HTTPS origin. `ClientRegistrationOptions(enabled=True)` is required for claude.ai Connectors.

Allowlist the host callbacks you actually use (Claude `https://claude.ai/api/mcp/auth_callback` / `https://claude.com/api/mcp/auth_callback`, Cursor `http://localhost:8787/callback`, Grok ephemeral `http://127.0.0.1:<port>/callback`). FastMCP's generic DCR docs still omit those four-host scars.

## Never

- Do not put a fleet `run_command` / mail / student plane on a public template server.
- Do not charge for this skill through Cursor official Marketplace.
