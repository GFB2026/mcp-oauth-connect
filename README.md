# MCP OAuth Connect

**Free checker** for when an MCP remote answers curl but dies in Claude / Cursor / Desktop / Grok Connectors.

Part of GFB's lab surface. Founder / peer identity (companies run with agents): [gregfredabytes.com](https://gregfredabytes.com/) · [essay](https://gregfredabytes.com/essay/agent-operated-companies/) · [what I run](https://gregfredabytes.com/running/)

The free checker reads metadata. It does not finish a handshake (no DCR, no token, no `tools/list`). That gap is real — treat a fail as a scoping signal, not a dead end.

Optional paid attach lab (four-client attempt + written path) lives on the studio product page, not here: https://gfbytes.com/products/mcp-oauth-connect/

On that page you can also paste a public HTTPS MCP URL and hit **Check** (`POST /products/diagnose`).

## Install (free)

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

Looks for a proper login challenge (not a bare 200 from curl), a registration endpoint, and S256. Paste **only the URL** in the Connectors UI — no API key.

## `template/`

Public ping-only example behind https://mcp.gfbytes.com (MIT). Reference server, not a service SKU.

## License

MIT for the plugin, skill, diagnose script, tests, and `template/`. Studio attach-lab / fix-round services are separate offers on gfbytes.com.
