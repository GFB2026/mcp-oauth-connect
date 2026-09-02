# Payment Link (seller)

- Product: `prod_V9pfxkWxzrujfU` (Four-host attach)
- Price: `price_1U9qko0hd61SUNoB2zK07NmT` ($149 USD one-time)
- Link: `plink_1U9qko0hd61SUNoBxceRWZZt` https://buy.stripe.com/3cI6oz64ybZJ2dP4ev3Nm0l
- Required field: `mcp_url` (MCP URL, text, 12–255, not optional)
- Retired: `price_1U9W0T0hd61SUNoB3cpQSW2t` / `plink_1U9W0U0hd61SUNoBluLZ6zGS` ($99, never paid, deactivated 2026-08-29)
- Success: https://gfbytes.com/products/mcp-oauth-connect/thank-you
- SKU metadata: `mcp_oauth_connect` / `gated_attach`

After pay: run diagnose.py on the checkout MCP URL. Pass → four-host transcript in two business days. Fail → quote. Do not issue a moc_live_ key. Do not add this SKU to gfb-rescue.
