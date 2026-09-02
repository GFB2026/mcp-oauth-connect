# MCP OAuth Connect

**Curl works. The Connectors UI does not.**

Your MCP server answers curl. Claude, Cursor, Desktop, and Grok still will not connect. This repo is the free checker.

For $149 we connect those four apps to your server and send screenshots within two business days: https://gfbytes.com/products/mcp-oauth-connect/

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

The checker looks for a proper login challenge on your server (not a 200 from curl), a registration endpoint, and S256. Paste **only the URL** in the Connectors UI — no API key.

If that check fails, do not buy the $149 pass. Ask for a quote instead.

## Paid — we'll connect it, $149 once

Checkout asks for your server URL. If the free check passes, we connect Claude, Cursor, Desktop, and Grok and send screenshots. One pass, two business days. We do not change your server.

## License

MIT.
