#!/usr/bin/env python3
"""Harvest Official MCP Registry remotes that fail diagnose.py.

Stdlib only (plus local diagnose.py). Writes JSONL candidates for outbound.
Does not send mail.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import diagnose  # noqa: E402

REGISTRY = "https://registry.modelcontextprotocol.io/v0.1/servers"


def _get(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "mcp-oauth-connect-harvest/0.1",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def iter_remotes(limit_servers: int) -> list[dict]:
    out: list[dict] = []
    cursor = None
    seen = 0
    while seen < limit_servers:
        q: dict[str, str | int] = {"limit": min(100, limit_servers - seen)}
        if cursor:
            q["cursor"] = cursor
        url = REGISTRY + "?" + urllib.parse.urlencode(q)
        payload = _get(url)
        rows = payload.get("servers") or []
        if not rows:
            break
        for row in rows:
            server = row.get("server") or {}
            name = server.get("name") or server.get("title") or ""
            remotes = server.get("remotes") or []
            for rem in remotes:
                rtype = (rem.get("type") or "").lower()
                rurl = rem.get("url") or ""
                if rtype not in {"streamable-http", "sse", "http"}:
                    continue
                if not rurl.startswith("https://"):
                    continue
                out.append({"name": name, "url": rurl, "type": rtype})
            seen += 1
            if seen >= limit_servers:
                break
        cursor = (payload.get("metadata") or {}).get("nextCursor")
        if not cursor:
            break
        time.sleep(0.2)
    dedup: dict[str, dict] = {}
    for item in out:
        dedup.setdefault(item["url"].rstrip("/"), item)
    return list(dedup.values())


def failing_checks(report: dict) -> list[str]:
    fails = []
    for name, check in (report.get("checks") or {}).items():
        if isinstance(check, dict) and check.get("ok") is False:
            fails.append(name)
    return fails


def hints(report: dict) -> list[str]:
    out = []
    for check in (report.get("checks") or {}).values():
        if isinstance(check, dict) and check.get("ok") is False and check.get("hint"):
            out.append(str(check["hint"])[:240])
    for w in report.get("warnings") or []:
        out.append(str(w)[:240])
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Harvest failing MCP remotes from the Official Registry"
    )
    p.add_argument(
        "--servers", type=int, default=80, help="Registry server rows to page"
    )
    p.add_argument(
        "--probe-limit", type=int, default=60, help="Max remotes to diagnose"
    )
    p.add_argument("--delay", type=float, default=0.4, help="Seconds between probes")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("data/failing_mcp_candidates.jsonl"),
        help="JSONL of failing remotes",
    )
    p.add_argument(
        "--all-out",
        type=Path,
        default=None,
        help="Optional JSONL of every probe",
    )
    args = p.parse_args(argv)

    remotes = iter_remotes(args.servers)[: args.probe_limit]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.all_out:
        args.all_out.parent.mkdir(parents=True, exist_ok=True)

    n_ok = n_fail = 0
    with ExitStack() as stack:
        fail_fh = stack.enter_context(args.out.open("w", encoding="utf-8"))
        all_fh = (
            stack.enter_context(args.all_out.open("w", encoding="utf-8"))
            if args.all_out
            else None
        )
        for i, item in enumerate(remotes, 1):
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                report = diagnose.diagnose(item["url"])
            except Exception as exc:  # noqa: BLE001
                report = {"ok": False, "error": str(exc)[:200], "checks": {}}
            row = {
                "ts": ts,
                "name": item["name"],
                "url": item["url"],
                "type": item["type"],
                "ok": bool(report.get("ok")),
                "failing_checks": failing_checks(report),
                "hints": hints(report),
                "error": report.get("error"),
            }
            if all_fh is not None:
                all_fh.write(json.dumps(row, separators=(",", ":")) + "\n")
            if row["ok"]:
                n_ok += 1
            else:
                n_fail += 1
                fail_fh.write(json.dumps(row, separators=(",", ":")) + "\n")
            print(
                f"[{i}/{len(remotes)}] {'ok' if row['ok'] else 'FAIL'} {item['url']}",
                file=sys.stderr,
            )
            time.sleep(args.delay)

    print(
        json.dumps(
            {
                "probed": len(remotes),
                "ok": n_ok,
                "fail": n_fail,
                "out": str(args.out),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
