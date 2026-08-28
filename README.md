# MCP OAuth Connect

**Curl works. The Connectors UI does not.** This plugin diagnoses why, and ships the allowlist-gated FastMCP OAuth 2.0 / DCR template that claude.ai, Claude Desktop, Cursor, and Grok actually complete.

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

- `/.well-known/oauth-authorization-server` with `registration_endpoint`
- Unauthenticated `/mcp` → **401** + `WWW-Authenticate: Bearer ... resource_metadata=`
- URL-only in the Connectors UI (no static bearer)

## Paid product (`template/`)

Allowlist-gated OAuth provider extracted from a production connector that already survives those four hosts. Copy `template/`, set `MCP_ISSUER_URL`, run with `MCP_OAUTH_DEV=1` until you have a key (`license/`).

**Do not buy this through Cursor official Marketplace** — that listing is free by contract. Keys are issued off-catalog. GFB already takes card on the live Stripe account behind `gfb-rescue` (`/api/checkout` SKUs). A `mcp_oauth_connect` price id is the missing env slot, not a new Stripe identity. See `license/README.md`.

Landing (operator desk, not studio): https://gregfredabytes.com/mcp-oauth-connect/

## What this is not

- Not a generic coding-skill dump
- Not the internal `gregops-plugins` marketplace
- Not a second bind onto `mcp.gregfredabytes.com`

## License

MIT for the plugin, skill, diagnose script, and tests. `template/` is proprietary (`LICENSE-TEMPLATE`).
