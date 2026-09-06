# Fulfillment — attach trace + fix rounds

The plugin skill, diagnose script, tests, and `template/` example are MIT. **$149 is the attach trace** — four-client attempt plus a written path — not a key to run `template/`. **Fix rounds are quoted after the trace** (typically $600–$1,500).

**Do not charge inside Cursor official Marketplace.** Charge on the landing Payment Link.

## Stripe (attach trace)

- Product: `prod_V9pfxkWxzrujfU` (rename display to MCP attach trace when convenient)
- Price: `price_1U9qko0hd61SUNoB2zK07NmT` ($149 USD one-time)
- Link: `plink_1U9qko0hd61SUNoBxceRWZZt` https://buy.stripe.com/3cI6oz64ybZJ2dP4ev3Nm0l
- Required custom field: `mcp_url` (MCP URL, 12–255 chars)
- Success: https://gfbytes.com/products/mcp-oauth-connect/thank-you
- Do **not** wire this SKU through `gfb-rescue`

## Attach-trace runbook ($149)

1. Buyer pays via the Payment Link (must paste MCP URL at checkout)
2. Success URL is `/products/mcp-oauth-connect/thank-you`
3. Run `diagnose.py` on that URL as a **scoping** step (pass or fail — both are valid buyers)
4. Attempt attach from GFB claude.ai / Desktop / Cursor / Grok
5. Deliver written attach trace per client within two business days (which step worked or died: 401 → PRM → AS → DCR → token → `tools/list`, with real responses). Screenshots are evidence.
6. **Refund** if we cannot attach **and** cannot say why
7. Do **not** run `license/issue.py` for this SKU

## Fix-round runbook (quoted)

1. Only after an attach trace (or equivalent written path)
2. Quote typically $600–$1,500 depending on IdP / DCR / consent / hosting work
3. Buyer approves quote before work
4. We change what is needed so Connectors attach; buyer reviews and merges
5. Out of $149 scope without a separate quote: Entra without DCR, custom IdPs, consent-UI flows, hosted tenancy, host tools (shell, mail, files, student data)

## Not this path

- No second Stripe identity
- No Cursor Marketplace charge
- No `moc_live_` license keys as the deliverable
