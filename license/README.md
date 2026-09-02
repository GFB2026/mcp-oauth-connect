# License / cash register (v0.3 attach)

The plugin skill, diagnose script, tests, and `template/` example are MIT. **$149 is a four-host attach**, not a key to run `template/`.

**Price: $149 one-time.** Not monthly. Not priced against Care/Rescue.

**Do not charge inside Cursor official Marketplace.** Cursor Publisher Terms §3.1. Cursor listing (if any) is diagnose-only. Charge on the landing Payment Link.

## v0.3 cash register

Stripe Payment Link on the existing GFB Stripe account. Same legal entity. No Gumroad. No second Stripe identity. Do **not** wire this SKU through `gfb-rescue` — rescue `publicBaseForSku` falls through to `/care`.

1. Buyer pays via the Payment Link on https://gfbytes.com/products/mcp-oauth-connect/
2. Success URL is `/products/mcp-oauth-connect/thank-you`
3. Greg emails the Stripe receipt address, collects the MCP URL, and attaches claude.ai / Desktop / Cursor / Grok
4. Do **not** run `license/issue.py` for this SKU. Keys are leftover from the extract offer (retired 2026-09-02). `issue.py` stays on disk for archaeology.

## Formats (legacy extract — do not sell)

- `MCP_OAUTH_DEV=1` — skip check on the public ping origin
- `moc_live_<email>|<unix_exp>.<hmac>` — retired for new payers
