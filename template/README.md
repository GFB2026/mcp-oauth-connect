# template/ — paid FastMCP OAuth provider

Ping-only FastMCP server with an allowlist-gated OAuth 2.0 / DCR provider.

Copy this directory. Set `MCP_ISSUER_URL`. Run with `MCP_OAUTH_DEV=1` until you have a key.

## Auto-approve residual (read this first)

Allowlist DCR closed attacker-controlled callbacks (GREGSTACK-CRIT-001 for redirect URIs). It did **not** add a consent screen.

Anyone who can reach `/register` + `/authorize` with an allowlisted redirect still gets an authorization code with **no human in the loop**. Loopback (`http://127.0.0.1:<port>/callback`, `MCP_ALLOW_LOOPBACK=1`) plus auto-approve is the remaining surface: if the origin is reachable without a tunnel/WAF, a local process can mint tokens.

That is acceptable while this template stays ping-only. It is dangerous the moment you wire host tools (shell, mail, files, student data). Before you add those tools: pin `MCP_ALLOWED_CLIENT_ID` after the first legitimate connect, set `MCP_ALLOW_LOOPBACK=0` if Grok is not a client, and do not expose the origin on the public internet without the same allowlist + tunnel posture the live connector uses.

This template is not a substitute for a real consent UI.

## Env

See `env.example`. License: `MCP_OAUTH_LICENSE_KEY` or `MCP_OAUTH_DEV=1`.
