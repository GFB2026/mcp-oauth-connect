# License / cash register (v0.4 gated attach)

The plugin skill, diagnose script, tests, and `template/` example are MIT. **$149 is a diagnose-gated four-host attach transcript**, not a key to run `template/`.

**Price: $149 one-time.** One round. Two business days. Not monthly. Not Care/Rescue.

**Do not charge inside Cursor official Marketplace.** Charge on the landing Payment Link.

## v0.4 cash register

Stripe Payment Link on the existing GFB Stripe account. Same legal entity. No Gumroad. No second Stripe identity. Do **not** wire this SKU through `gfb-rescue`.

Product: `prod_V9pfxkWxzrujfU` (name: Four-host attach)
Price: `price_1U9qko0hd61SUNoB2zK07NmT` ($149)
Link: `plink_1U9qko0hd61SUNoBxceRWZZt` https://buy.stripe.com/3cI6oz64ybZJ2dP4ev3Nm0l
Required custom field: `mcp_url` (MCP URL, 12–255 chars)

1. Buyer pays via the Payment Link (must paste MCP URL at checkout)
2. Success URL is `/products/mcp-oauth-connect/thank-you`
3. Greg runs `diagnose.py` on that URL
4. Pass → attach from GFB claude.ai / Desktop / Cursor / Grok → deliver transcript (four connected screenshots + handshake capture) within two business days
5. Fail → quote a separate fix round. Entra without DCR, custom IdPs, consent UI, hosted tenancy, host tools are out of the $149 round
6. Do **not** run `license/issue.py` for this SKU
