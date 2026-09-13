# GitHub Copilot — this repo

This repository is a **free MCP OAuth diagnostic checker** (CLI + plugin skill).

## What it is

- Product claim: remotes that pass `curl` still fail Claude / Cursor / Desktop / Grok Connectors.
- `skills/mcp-oauth-connect/scripts/diagnose.py` is **stdlib-only**. Do not add third-party deps to it.
- The free path is **metadata-only**. It does not finish a handshake.
- Tests live in `tests/` and must stay **offline** (mock HTTP). Run `python -m pytest`.
- `template/` is a ping-only reference server, not a hosted SKU.
- Paid attach-lab copy belongs on gfbytes.com, not in this tree.
- MIT. No secrets, no private company internals.

## Safe edit lanes

Docs, tests, GitHub Actions workflows, GitHub Copilot config (this file, `.copilotignore`, `.github/workflows/copilot-setup-steps.yml`), and README clone/run copy.

## NEVER

- Secrets, tokens, `.env` files, or credentials
- Live deploy
- `gc-mcp`, fleet, `/opt/apps`, or ops surfaces
- Handshake creep on the free checker: DCR, token mint, or `tools/list`
- Third-party dependencies on `diagnose.py`
- Private company internals
- Student or mail bodies
