# MCP OAuth Connect

**Curl works. The Connectors UI does not.** This plugin diagnoses why.

Free diagnose skill (MIT). **$149 is a four-host attach on your origin** — not a zip of `template/`.

`template/` is the public ping-only example behind `https://mcp.gfbytes.com`. It is not the paid SKU. ILI / GregOps stays private. This repo has **no** host shell, mail, or student tools.

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

## Paid — four-host attach, $149 one-time

You send the MCP URL. GFB makes **claude.ai, Desktop, Cursor, and Grok** Connectors attach to that origin. Fulfillment is the four hosts connecting, not a license key and not a file drop.

Stripe Payment Link on the existing GFB account. Not monthly. Not a Cursor Marketplace charge (Publisher Terms §3.1).

Buy: https://gfbytes.com/products/mcp-oauth-connect/

## What this is not

- Not a zip of `template/`
- Not a generic coding-skill dump
- Not the internal `gregops-plugins` marketplace
- Not a second bind onto `mcp.gregfredabytes.com` (operator bus). Public proof is `https://mcp.gfbytes.com` (ping only)
- Not a rescue/Care SKU
- Not a Cursor Marketplace charge

## License

MIT for the plugin, skill, diagnose script, tests, and `template/` example. Cursor official Marketplace, if listed, is the diagnose skill only — do not submit this tree as a paid plugin. Catalog freeze: no new catalog submissions until an attach payer exists.
