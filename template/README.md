# template/ — FastMCP OAuth reference (not the $149 SKU)

Ping-only FastMCP server with an allowlist-gated OAuth 2.0 / DCR provider.

This directory is the public ping-only example behind https://mcp.gfbytes.com. It is MIT. The **gfbytes paid offer is the connection report** (screenshots from GFB accounts), not a sale of this tree. Copy this directory to wire your own ping-only origin. Set `MCP_ISSUER_URL`. `MCP_OAUTH_DEV=1` skips any local license gate leftover from earlier packaging.

## Auto-approve residual (read this first)

Allowlist DCR closed attacker-controlled callbacks (GREGSTACK-CRIT-001 for redirect URIs). It did **not** add a consent screen.

Anyone who can reach `/register` + `/authorize` with an allowlisted redirect still gets an authorization code with **no human in the loop**. Loopback (`http://127.0.0.1:<port>/callback`, `MCP_ALLOW_LOOPBACK=1`) plus auto-approve is the remaining surface: if the origin is reachable without a tunnel/WAF, a local process can mint tokens.

That is acceptable while this template stays ping-only. It is dangerous the moment you wire host tools (shell, mail, files, student data). Before you add those tools: pin `MCP_ALLOWED_CLIENT_ID` after the first legitimate connect, set `MCP_ALLOW_LOOPBACK=0` if Grok is not a client, and do not expose the origin on the public internet without the same allowlist + tunnel posture the live connector uses.

This template is not a substitute for a real consent UI.

## Env

See `env.example`. Optional local gate leftovers: `MCP_OAUTH_LICENSE_KEY` or `MCP_OAUTH_DEV=1`. Not part of the gfbytes connection-report SKU.
