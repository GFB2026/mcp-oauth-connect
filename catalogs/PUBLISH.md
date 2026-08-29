# Catalog pack — MCP OAuth Connect (diagnose origin)

List the **public ping origin** and the **free diagnose skill**. Do not list `template/` as a paid catalog SKU.

Canonical product: https://gfbytes.com/products/mcp-oauth-connect/
Demo MCP: https://mcp.gfbytes.com/mcp
Repo: https://github.com/GFB2026/mcp-oauth-connect
server.json: this directory
server-card: https://mcp.gfbytes.com/.well-known/mcp/server-card.json

## Official MCP Registry

Namespace `com.gfbytes/mcp-oauth-connect` needs DNS or HTTP proof that GFB controls gfbytes.com.

```text
mcp-publisher login dns --domain gfbytes.com
mcp-publisher publish
```

Until that TXT/HTTP challenge is in DNS, do not claim a registry row exists.

## Smithery

https://smithery.ai/new — HTTPS URL `https://mcp.gfbytes.com/mcp` (OAuth, streamable HTTP). Scan may need a one-time auth. Static card is at `/.well-known/mcp/server-card.json`.

## Glama

https://glama.ai/mcp/servers — add GitHub `GFB2026/mcp-oauth-connect`. Claim the listing. Do not paste fleet MCP.

## PulseMCP

https://www.pulsemcp.com/submit — prefers Official Registry ingest. After registry publish, wait a week or email hello@pulsemcp.com.

## Host catalogs (free diagnose only)

| Host | Status |
|------|--------|
| Own GitHub marketplace | Live: `/plugin marketplace add GFB2026/mcp-oauth-connect` |
| Grok official | PR https://github.com/xai-org/plugin-marketplace/pull/410 — pin HEAD after this ship |
| Cursor official | Greg login https://cursor.com/marketplace/publish — diagnose only, dual-license tree is a reject risk |
| Claude directory | Greg login https://platform.claude.com/plugins/submit |

## Not this pack

- mcp.gregfredabytes.com
- Care / gfb-rescue SKUs
- Charging inside a first-party marketplace
