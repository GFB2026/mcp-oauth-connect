# Maker first comment (do not hunt until this is pasted live)

Hey Product Hunt — I'm Greg. I run connectors for a living and kept hitting the same wall: curl against `/mcp` looks fine, then claude.ai / Desktop / Cursor / Grok Connectors UI dies on OAuth discovery.

The scars are boring and specific. Origin PRM 404. Relative `resource_metadata` on the 401. Cross-host 3xx. Static bearer in `mcp.json`. Desktop stripping JSON `url`. Grok wanting a public client on loopback `/callback` with S256.

So this is a diagnose skill plus a live ping-only origin at mcp.gfbytes.com that already survives those four hosts. Install is free. The paid piece is a FastMCP `template/` extract, off-catalog, not a Cursor Marketplace charge.

I'd love eyes on the handshake, not upvotes. Probe it, break it, tell me which host still lies.

Site: https://gfbytes.com/products/mcp-oauth-connect/
