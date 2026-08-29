# Catalog pack — MCP OAuth Connect (diagnose origin)

List the **public ping origin** and the **free diagnose skill**. Do not list `template/` as a paid catalog SKU.

Canonical product: https://gfbytes.com/products/mcp-oauth-connect/
Demo MCP: https://mcp.gfbytes.com/mcp
Repo: https://github.com/GFB2026/mcp-oauth-connect
server.json: this directory
server-card: https://mcp.gfbytes.com/.well-known/mcp/server-card.json

## Official MCP Registry

**LIVE** `com.gfbytes/mcp-oauth-connect` `0.2.0` (active 2026-08-29).
Search: `https://registry.modelcontextprotocol.io/v0.1/servers?search=com.gfbytes/mcp-oauth-connect`
HTTP proof: `https://gfbytes.com/.well-known/mcp-registry-auth` (Ed25519). Private key stays on gfb `/root/.config/mcp-publisher/` — not git.

Republish:

```text
HOME=/root mcp-publisher login http --domain=gfbytes.com --private-key=$(cat /root/.config/mcp-publisher/gfbytes-ed25519.hex)
HOME=/root mcp-publisher publish /opt/apps/gfb/products/mcp-oauth-connect/catalogs/server.json
```

`server.json` description must stay ≤100 chars (schema).

## Smithery

**LIVE** https://smithery.ai/servers/greg-efcm/mcp-oauth-connect (external, `https://mcp.gfbytes.com/mcp`). Namespace is Smithery’s `greg-efcm` (3-namespace cap blocked `gfbytes`). Republish: `smithery mcp publish https://mcp.gfbytes.com/mcp -n greg-efcm/mcp-oauth-connect`.

## Glama

https://glama.ai/mcp/servers — add GitHub `GFB2026/mcp-oauth-connect`. Claim the listing. Do not paste fleet MCP.

## PulseMCP

https://www.pulsemcp.com/submit — prefers Official Registry ingest. After registry publish, wait a week or email hello@pulsemcp.com.

## Host catalogs (free diagnose only)

| Host | Status |
|------|--------|
| Own GitHub marketplace | Live: `/plugin marketplace add GFB2026/mcp-oauth-connect` |
| Official MCP Registry | Live: `com.gfbytes/mcp-oauth-connect` 0.2.0 |
| Smithery | Live: https://smithery.ai/servers/greg-efcm/mcp-oauth-connect |
| Grok official | PR https://github.com/xai-org/plugin-marketplace/pull/410 — pin `28a9e8a` |
| Cursor official | Do **not** submit this dual-license tree (`LISTING.md`). Form is Greg login https://cursor.com/marketplace/publish |
| Claude directory | `claude plugin validate` passed. Form is Greg Console https://platform.claude.com/plugins/submit |

## Not this pack

- mcp.gregfredabytes.com
- Care / gfb-rescue SKUs
- Charging inside a first-party marketplace
