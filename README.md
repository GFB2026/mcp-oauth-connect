# MCP OAuth Connect

**Find out why four clients won't attach.**

The free checker reads metadata. It never finishes a handshake (no DCR, no token, no `tools/list`). That gap is the product.

For **$149** we attempt Claude, Cursor, Desktop, and Grok against your server and send an **attach trace** — which step worked or died, in which client, with real responses. Failures welcome. If we can't attach and can't say why, you get your money back.

After the trace, **fix rounds** are quoted separately (typically $600–$1,500): we make it attach; you merge the patch.

Buy / fulfill: https://gfbytes.com/products/mcp-oauth-connect/

On the product page, paste any public HTTPS MCP URL and hit **Check** — that hits `POST /products/diagnose` (server-side `diagnose.py`). Failures are the intended $149 buyers.

Outbound targeting (no auto-send): `ph/OUTBOUND_TARGETING.md`. Harvest: `python skills/mcp-oauth-connect/scripts/harvest_failing.py`.

## Install (free checker)

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

If that check fails, **that's what the $149 attach-trace round is for.**

## Attach trace — $149 once

Checkout asks for your server URL. We attempt all four clients and deliver a written path (401 → PRM → AS → DCR → token → `tools/list`) per client within two business days. Screenshots are evidence, not the product.

## Fix round — quoted

After the trace, we quote a separate fix. Not included in $149. Out of scope for the $149 round without a separate quote: Entra without DCR, custom IdPs, consent-UI flows, hosted tenancy, host tools.

## `template/`

Public ping-only example behind https://mcp.gfbytes.com (MIT). Reference server, not the paid SKU.

## License

MIT for the plugin, skill, diagnose script, tests, and `template/`. The $149 offer and fix rounds are services on gfbytes.
