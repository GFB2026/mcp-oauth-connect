# License (v0.1 register)

The plugin skill and diagnose script are free (MIT). `template/` is the paid extract.

**Price: $149 one-time, 365-day key.** Not monthly. Not priced against Care/Rescue. $99 was an unowned Cursor commit (2026-08-28); replaced 2026-08-29.

**Do not charge inside Cursor official Marketplace.** Cursor Publisher Terms §3.1: listings are free; no fees directly or indirectly for a Plugin through the Marketplace. Cursor listing (if any) is diagnose-only. Charge on the landing Payment Link.

## v0.1 cash register

Stripe Payment Link on the existing GFB Stripe account. Same legal entity. No Gumroad. No second Stripe identity. Do **not** wire `STRIPE_PRICE_MCP_OAUTH` through `gfb-rescue` until a payer exists — rescue `publicBaseForSku` falls through to `/care` and the webhook creates an intake order. A digital good on the Care form is a defect.

1. Buyer pays via the Payment Link on https://gregfredabytes.com/mcp-oauth-connect/
2. Success URL is `/mcp-oauth-connect/thank-you`
3. You run `python license/issue.py buyer@example.com 365` on the seller machine (`MCP_OAUTH_LICENSE_SECRET` set)
4. Paste the printed key into the Stripe Payment Link fulfillment note / a one-line email

`issue.py` does not call Stripe.

## After the first payer

Then, and only then: add `mcp_oauth_connect` to the rescue price map and webhook key mail. Not before.

## Formats

- `MCP_OAUTH_DEV=1` — skip check (honor system; this is not DRM)
- `moc_live_<email>|<unix_exp>.<hmac>` — issued by `issue.py`
- Without `MCP_OAUTH_LICENSE_SECRET`, `check.py` only reminds — any `moc_live_` string longer than 20 characters passes
