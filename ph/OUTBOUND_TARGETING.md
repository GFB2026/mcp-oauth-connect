# Outbound targeting — MCP attach trace / fix rounds

Do **not** send from this file alone. Every mail needs Greg’s send phrase + `/armed-check` + `desk.act approve_send`. Harvest does not send mail.

## ICP

Already ships an **HTTPS MCP** remote. Trying to get **claude.ai / Desktop / Cursor / Grok Connectors** to attach. Stuck in **curl works / UI fails**.

Not: ILI students, “learn MCP” beginners, stdio-only local tools.

### Pain signals (map to `diagnose.py` fails)

- No `WWW-Authenticate` + PRM (static bearer pattern)
- Relative `resource_metadata`
- Origin PRM 404
- Missing `registration_endpoint` / S256
- Cross-host 3xx on `/mcp`
- Unauthenticated GET `/mcp` returns 200

## Offer ladder (what we sell them)

1. Free checker (this repo)
2. **$149 attach trace** — four real clients; failures welcome; refund if we can’t say why
3. **Quoted fix round** (~$600–$1,500) after the trace

## Channels (ranked)

| Rank | Source | Motion |
|------|--------|--------|
| 1 | Official MCP Registry remotes that **fail** harvest | Cold note with *their* failing checks |
| 2 | GitHub issues/discussions (`Connectors`, `oauth-protected-resource`, `WWW-Authenticate`, `DCR`) | Soft reply + diagnose snippet first |
| 3 | X / Discord / Reddit “curl works Claude doesn’t” | Soft reply |
| 4 | Smithery / Glama / PulseMCP remotes | Same JSONL schema after registry yield proven |
| 5 | Inbound (page probe + Stripe `mcp_url`) | Fulfill first |

## Harvest

```bash
cd mcp-oauth-connect
python skills/mcp-oauth-connect/scripts/harvest_failing.py \
  --servers 80 --probe-limit 60 \
  --out data/failing_mcp_candidates.jsonl \
  --all-out data/all_mcp_probes.jsonl
```

Yield kill: after ~100 probes, if fail rate &lt; ~15%, change source or stop.

**Seed run 2026-09-06:** 25 remotes probed from Official Registry → **21 fail / 4 ok (84% fail)**. Top fails: `unauthenticated_mcp_post`, path-appended PRM, absolute `resource_metadata`, AS metadata / S256. Output: `data/failing_mcp_candidates.jsonl` (gitignored).

## Motion (no blast)

1. Qualify: harvest row with ≥1 connector-critical fail  
2. Enrich lightly from registry metadata only (no scraped PII dumps)  
3. One touch / domain / 14 days until reply; stop on opt-out  
4. First touch = free checker + their fails; $149 only as optional next step  
5. Fix round only after they ask / after a paid trace  

## Copy skeleton (draft — not sent)

> Saw `https://…` on the MCP registry. Free checker says: &lt;fail1&gt;, &lt;fail2&gt;. That pattern usually passes curl and dies in Connectors. Checker: https://github.com/GFB2026/mcp-oauth-connect — or paste the URL into https://gfbytes.com/products/mcp-oauth-connect/ and hit Check. If you want four-client proof, the attach trace is $149 (refund if we can’t say why).

## Metrics

Harvest fail % → touches → replies → paid traces → fix quotes → closes.

## Human gates

- No autopilot mail / Tasks blast from harvest  
- Greg send phrase + `/armed-check` before any outbound  
- Payment Link and price unchanged; Stripe product display is **MCP attach trace**
