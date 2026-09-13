This repo is a free MCP OAuth diagnostic checker (CLI + plugin skill).

- Product claim: remotes that pass `curl` still fail Claude / Cursor / Desktop / Grok Connectors.
- `skills/mcp-oauth-connect/scripts/diagnose.py` is stdlib-only. Do not add third-party deps to it.
- The checker reads discovery metadata. Do not add DCR, token mint, or `tools/list` to the free path.
- Tests live in `tests/` and must stay offline (mock HTTP). Run `python -m pytest`.
- `template/` is a ping-only reference server, not a hosted SKU.
- Paid attach-lab copy belongs on gfbytes.com, not in this tree.
- MIT. No secrets, no private company internals.
