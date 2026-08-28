# License (cash register)

The plugin skill and diagnose script are free. `template/` is the paid product.

**Do not charge inside Cursor official Marketplace.** Cursor Publisher Terms §3.1: listings are free. Charge here (Stripe Payment Link / MCP Marketplace license / Gumroad) and keep the Cursor listing as a free install of the diagnose skill.

## v0.1 (no live Stripe yet)

1. Set `MCP_OAUTH_LICENSE_SECRET` on the seller machine only.
2. `python license/issue.py buyer@example.com 365`
3. Buyer sets `MCP_OAUTH_LICENSE_KEY` to that value (or `MCP_OAUTH_DEV=1` while building).
4. Cash register already on the stack: GFB Stripe via `gfb-rescue` (`STRIPE_SECRET_KEY` + `POST /api/checkout` with `sku`). Add `STRIPE_PRICE_MCP_OAUTH` / `mcp_oauth_connect` to that map when the live Price exists. Do not open a second Stripe account. Studio checkout stays on gfbytes.com/care; this SKU is operator product.

## Formats

- `MCP_OAUTH_DEV=1` — skip check
- `moc_live_<email>|<unix_exp>.<hmac>` — issued by `issue.py`
