# MCP OAuth Connect

**Curl works. The Connectors UI does not.** This plugin diagnoses why. The scarce asset is the four-host scars FastMCP's generic DCR docs still omit, a diagnose script aimed at the Connectors UI failure mode, and proof that this provider already survives claude.ai, Desktop, Cursor, and Grok on a live origin.

`template/` is a mechanical extract of a production connector. It is not DRM. `MCP_OAUTH_DEV=1` skips the license check. Treat a payer as a kill-rule test, not as a product line next to ILI.

ILI / GregOps stays private. This repo has **no** host shell, mail, or student tools.

## Install (free — diagnose skill)

Claude Code:

```text
/plugin marketplace add GFB2026/mcp-oauth-connect
/plugin install mcp-oauth-connect@mcp-oauth-connect
```

Grok Build:

```text
grok plugin marketplace add GFB2026/mcp-oauth-connect
grok plugin install mcp-oauth-connect --trust
```

Then:

```bash
python skills/mcp-oauth-connect/scripts/diagnose.py https://your-mcp.example
```

You need:

- `/.well-known/oauth-authorization-server` with `registration_endpoint` and `"code_challenge_methods_supported": ["S256"]`
- RFC 9728 PRM at `/.well-known/oauth-protected-resource` and/or `/.well-known/oauth-protected-resource/mcp`
- Unauthenticated `GET /mcp` → **401** or **405**; `POST /mcp` → **401** + `WWW-Authenticate: Bearer ... resource_metadata=<absolute https url>`
- No cross-host `3xx` on the MCP path
- URL-only in the Connectors UI (no static bearer)

## Paid extract (`template/`) — $149 one-time

Allowlist-gated OAuth provider extracted from a production connector that already survives those four hosts. Copy `template/`, set `MCP_ISSUER_URL`, run with `MCP_OAUTH_DEV=1` until you have a key (`license/`).

**$149 one-time, 365-day key**, Stripe Payment Link on the existing GFB account. Not monthly. Not a Cursor Marketplace charge (Publisher Terms §3.1). Keys are issued off-catalog with `license/issue.py`.

Landing (Buy lives here): https://gregfredabytes.com/mcp-oauth-connect/

The public default allowlist is slightly more Cursor-ready than production (it includes `http://localhost:8787/callback`). Auto-approve is unchanged — read `template/README.md` before wiring host tools.

## What this is not

- Not a generic coding-skill dump
- Not the internal `gregops-plugins` marketplace
- Not a second bind onto `mcp.gregfredabytes.com` (that origin is the operator bus). Public proof is `https://mcp.gfbytes.com` (ping only).
- Not a rescue/Care SKU (that map is for after a payer exists)
- Not a second plugin, hosted diagnose tenant, or NY CE-ops pack

## License

MIT for the plugin, skill, diagnose script, and tests. `template/` is proprietary (`LICENSE-TEMPLATE`). Cursor official Marketplace, if listed, is the diagnose skill only — do not submit this dual-licensed tree as a paid plugin.
