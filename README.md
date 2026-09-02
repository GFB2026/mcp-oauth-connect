# MCP OAuth Connect

**Curl works. The Connectors UI does not.** This plugin diagnoses why.

Free diagnose skill (MIT). **$149 is a diagnose-gated four-host attach transcript** — not a zip of `template/`.

`template/` is the public ping-only example behind `https://mcp.gfbytes.com`. Handshake/curl proof only. ILI / GregOps stays private. This repo has **no** host shell, mail, or student tools.

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

**Attach is only for origins that pass this probe.** Failing origins get a quote, not the $149 round.

## Paid — four-host attach transcript, $149 one-time

Checkout collects the **MCP URL**. GFB runs diagnose.py. If it passes, GFB attaches from GFB-controlled **claude.ai, Desktop, Cursor, and Grok** and delivers a transcript (four connected screenshots + handshake capture). One round. Two business days. No server code, no IdP config, no consent UI, no hosted tenancy.

If diagnose fails: quote, not uncapped consulting.

Stripe Payment Link on the existing GFB account. Not monthly. Not a Cursor Marketplace charge (Publisher Terms §3.1).

Buy: https://gfbytes.com/products/mcp-oauth-connect/

## What this is not

- Not a zip of `template/`
- Not a generic coding-skill dump
- Not the internal `gregops-plugins` marketplace
- Not a second bind onto `mcp.gregfredabytes.com` (operator bus). Public proof is `https://mcp.gfbytes.com` (ping / handshake only)
- Not a rescue/Care SKU
- Not a Cursor Marketplace charge
- Not server-side OAuth implementation, Entra-without-DCR, or a hosted tenant

## License

MIT for the plugin, skill, diagnose script, tests, and `template/` example. Cursor official Marketplace, if listed, is the diagnose skill only. Catalog freeze: no new catalog submissions until an attach payer exists.
