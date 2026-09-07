#!/usr/bin/env python3
"""Probe an MCP HTTPS URL for OAuth 2.0 / DCR that Connectors UIs actually need.

Stdlib only. Exit 0 if the connector-critical checks pass; 1 otherwise.

Checks match Anthropic's connector troubleshooting page, not merely
"is OAuth implemented":
  - RFC 8414 AS metadata (or OIDC discovery fallback)
  - code_challenge_methods_supported includes S256
  - RFC 9728 protected-resource metadata (origin and/or path-appended)
  - no cross-host 3xx on the MCP path
  - unauthenticated GET /mcp is 401 or 405 (405 is fine; Streamable HTTP is POST)
  - unauthenticated POST /mcp is either:
      * 401 + WWW-Authenticate Bearer + resource_metadata (older clients), or
      * 200 JSON-RPC initialize/discover result (MCP 2026-07-28 anonymous discovery)
  - resource_metadata is an absolute HTTPS URL (401 header, else origin well-known PRM)
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urljoin, urlparse

REQUIRED_AS_KEYS = ("issuer", "authorization_endpoint", "token_endpoint", "registration_endpoint")
_RESOURCE_METADATA_RE = re.compile(
    r"resource_metadata\s*=\s*(?:\"([^\"]+)\"|'([^']+)'|([^\s,;]+))",
    re.I,
)


def _init_body(protocol_version: str) -> bytes:
    return json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": protocol_version,
                "capabilities": {},
                "clientInfo": {"name": "mcp-oauth-connect-diagnose", "version": "0.3.0"},
                "_meta": {"io.modelcontextprotocol/protocolVersion": protocol_version},
            },
        }
    ).encode("utf-8")


_INIT_BODY = _init_body("2025-03-26")
_INIT_BODY_2026 = _init_body("2026-07-28")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, hdrs):
        raise urllib.error.HTTPError(req.full_url, code, msg, hdrs, fp)

    http_error_302 = http_error_301
    http_error_303 = http_error_301
    http_error_307 = http_error_301
    http_error_308 = http_error_301


def _headers_dict(hdrs) -> dict[str, str]:
    return {str(k).lower(): str(v) for k, v in (hdrs.items() if hdrs else [])}


def _resource_metadata_url(www: str) -> str | None:
    m = _RESOURCE_METADATA_RE.search(www or "")
    if not m:
        return None
    return next((g for g in m.groups() if g), None)


def _is_absolute_https(url: str) -> bool:
    p = urlparse(url)
    return p.scheme == "https" and bool(p.netloc)


def _cross_host(from_url: str, location: str | None) -> bool:
    if not location:
        return False
    loc = urlparse(urljoin(from_url, location))
    src = urlparse(from_url)
    return bool(loc.netloc) and loc.netloc.lower() != src.netloc.lower()


def _split_origin_mcp(base: str) -> tuple[str, str]:
    parsed = urlparse(base.strip())
    origin = f"{parsed.scheme}://{parsed.netloc}"
    path = (parsed.path or "").rstrip("/")
    mcp_url = origin + (path if path else "/mcp")
    return origin, mcp_url


def _prm_path_url(origin: str, mcp_url: str) -> str:
    path = urlparse(mcp_url).path.lstrip("/")
    if not path:
        return urljoin(origin + "/", ".well-known/oauth-protected-resource")
    return urljoin(origin + "/", ".well-known/oauth-protected-resource/" + path)


def _request(
    method: str,
    url: str,
    data: bytes | None = None,
    timeout: float = 12.0,
    content_type: str | None = None,
    extra_headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, str], bytes, str | None]:
    headers = {"User-Agent": "mcp-oauth-connect/0.3"}
    if extra_headers:
        headers.update(extra_headers)
    if data is not None:
        headers["Content-Type"] = content_type or "application/json"
        headers.setdefault("Accept", "application/json, text/event-stream")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    ctx = ssl.create_default_context()
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), _NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as resp:
            loc = resp.headers.get("Location") or resp.headers.get("location")
            return resp.status, _headers_dict(resp.headers), resp.read(), loc
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        loc = e.headers.get("Location") or e.headers.get("location") if e.headers else None
        return e.code, _headers_dict(e.headers), body, loc


def _load_json(body: bytes) -> dict[str, Any]:
    try:
        data = json.loads(body.decode("utf-8", errors="replace") if body else "{}")
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _jsonrpc_result(body: bytes) -> dict[str, Any] | None:
    parsed = _load_json(body)
    if parsed.get("jsonrpc") != "2.0":
        text = body.decode("utf-8", errors="replace") if body else ""
        parsed = {}
        for line in text.splitlines():
            if line.startswith("data:"):
                parsed = _load_json(line[5:].strip().encode("utf-8"))
                if parsed.get("jsonrpc") == "2.0":
                    break
    if parsed.get("jsonrpc") != "2.0":
        return None
    result = parsed.get("result")
    return result if isinstance(result, dict) else None


def _looks_like_mcp_hello(result: dict[str, Any]) -> bool:
    if not result:
        return False
    if result.get("protocolVersion") or result.get("serverInfo"):
        return True
    if result.get("resultType") == "complete" and result.get("supportedVersions"):
        return True
    caps = result.get("capabilities")
    return isinstance(caps, dict)


def _prm_check(url: str) -> dict[str, Any]:
    status, _headers, body, location = _request("GET", url)
    parsed = _load_json(body)
    ok = status == 200 and bool(parsed)
    return {
        "ok": ok,
        "url": url,
        "status": status,
        "location": location,
        "resource": parsed.get("resource"),
        "authorization_servers": parsed.get("authorization_servers"),
        "hint": None
        if ok
        else "Need HTTP 200 JSON (RFC 9728). Claude probes this path during Connectors discovery.",
    }


def diagnose(base: str) -> dict[str, Any]:
    raw = base.strip()
    parsed = urlparse(raw)
    if parsed.scheme != "https" or not parsed.netloc:
        return {
            "ok": False,
            "error": "URL must be https (Connectors UI will not complete OAuth over http)",
            "url": raw,
        }

    origin, mcp_url = _split_origin_mcp(raw)
    as_url = urljoin(origin + "/", ".well-known/oauth-authorization-server")
    oidc_url = urljoin(origin + "/", ".well-known/openid-configuration")
    prm_origin_url = urljoin(origin + "/", ".well-known/oauth-protected-resource")
    prm_path_url = _prm_path_url(origin, mcp_url)

    report: dict[str, Any] = {
        "url": origin,
        "mcp_url": mcp_url,
        "as_url": as_url,
        "checks": {},
        "ok": True,
        "warnings": [],
    }

    status, _headers, body, _loc = _request("GET", as_url)
    as_json = _load_json(body)
    missing = [k for k in REQUIRED_AS_KEYS if not as_json.get(k)]
    as_ok = status == 200 and not missing
    if not as_ok:
        oidc_status, _h, oidc_body, _l = _request("GET", oidc_url)
        oidc_json = _load_json(oidc_body)
        oidc_missing = [k for k in REQUIRED_AS_KEYS if not oidc_json.get(k)]
        if oidc_status == 200 and not oidc_missing:
            as_ok = True
            as_json = oidc_json
            missing = []
            as_url = oidc_url
            report["as_url"] = oidc_url
            report["warnings"].append("AS metadata served at openid-configuration, not oauth-authorization-server")
    report["checks"]["authorization_server_metadata"] = {
        "ok": as_ok,
        "status": status,
        "missing": missing,
        "issuer": as_json.get("issuer"),
        "registration_endpoint": as_json.get("registration_endpoint"),
    }
    if not as_ok:
        report["ok"] = False

    methods = as_json.get("code_challenge_methods_supported") or []
    s256_ok = isinstance(methods, list) and "S256" in methods
    report["checks"]["code_challenge_s256"] = {
        "ok": s256_ok,
        "code_challenge_methods_supported": methods,
        "hint": None
        if s256_ok
        else 'Authorization server metadata must advertise "code_challenge_methods_supported": ["S256"]. Claude sends PKCE S256 on every authorize.',
    }
    if not s256_ok:
        report["ok"] = False

    prm_origin = _prm_check(prm_origin_url)
    prm_path = _prm_check(prm_path_url)
    prm_any = prm_origin["ok"] or prm_path["ok"]
    report["checks"]["protected_resource_metadata"] = prm_origin
    report["checks"]["protected_resource_metadata_path"] = prm_path
    report["checks"]["protected_resource_metadata_any"] = {
        "ok": prm_any,
        "hint": None
        if prm_any
        else "Need RFC 9728 JSON at /.well-known/oauth-protected-resource and/or the path-appended form (.../oauth-protected-resource/mcp).",
    }
    if not prm_any:
        report["ok"] = False
    elif not prm_origin["ok"]:
        report["warnings"].append(
            "Origin PRM 404; path-appended form is present. Anthropic also curls /.well-known/oauth-protected-resource"
        )
    elif not prm_path["ok"] and urlparse(mcp_url).path not in ("", "/"):
        report["warnings"].append(
            "Path-appended PRM missing. Claude probes /.well-known/oauth-protected-resource/<mcp-path>"
        )

    get_status, get_headers, _get_body, get_loc = _request("GET", mcp_url)
    post_status, post_headers, post_body, post_loc = _request(
        "POST",
        mcp_url,
        data=_INIT_BODY,
        extra_headers={"MCP-Protocol-Version": "2025-03-26"},
    )
    post26_status, post26_headers, post26_body, post26_loc = _request(
        "POST",
        mcp_url,
        data=_INIT_BODY_2026,
        extra_headers={
            "MCP-Protocol-Version": "2026-07-28",
            "Mcp-Method": "initialize",
        },
    )

    cross = (
        _cross_host(mcp_url, get_loc)
        or _cross_host(mcp_url, post_loc)
        or _cross_host(mcp_url, post26_loc)
    )
    redirect_ok = not cross
    report["checks"]["mcp_no_cross_host_redirect"] = {
        "ok": redirect_ok,
        "get_status": get_status,
        "get_location": get_loc,
        "post_status": post_status,
        "post_location": post_loc,
        "post_2026_07_28_status": post26_status,
        "post_2026_07_28_location": post26_loc,
        "hint": None
        if redirect_ok
        else "MCP URL 3xx to a different host drops Authorization. Register the final URL.",
    }
    if not redirect_ok:
        report["ok"] = False

    get_ok = get_status in (401, 405)
    if get_status == 200:
        get_ok = False
    report["checks"]["unauthenticated_mcp_get"] = {
        "ok": get_ok,
        "status": get_status,
        "hint": None
        if get_ok
        else "GET /mcp should be 401 (challenge) or 405 (POST-only Streamable HTTP). HTTP 200 without auth is the curl-pass / UI-fail pattern.",
    }
    if not get_ok:
        report["ok"] = False

    www = (
        post_headers.get("www-authenticate")
        or post26_headers.get("www-authenticate")
        or get_headers.get("www-authenticate")
        or ""
    )
    meta = _resource_metadata_url(www)

    challenge_ok = post_status == 401 and "bearer" in www.lower() and bool(meta)
    if not challenge_ok and post26_status == 401:
        www26 = post26_headers.get("www-authenticate") or ""
        meta26 = _resource_metadata_url(www26)
        if "bearer" in www26.lower() and meta26:
            challenge_ok = True
            www = www26
            meta = meta26

    hello = _jsonrpc_result(post26_body) or _jsonrpc_result(post_body)
    anon_ok = (
        (post26_status == 200 or post_status == 200)
        and _looks_like_mcp_hello(hello or {})
    )

    if challenge_ok and anon_ok:
        mode = "version_gate"
    elif anon_ok:
        mode = "anonymous_discovery_2026-07-28"
    elif challenge_ok:
        mode = "oauth_challenge"
    else:
        mode = "miss"

    post_ok = mode != "miss"
    report["checks"]["unauthenticated_mcp_post"] = {
        "ok": post_ok,
        "mode": mode,
        "status": post_status,
        "status_2026_07_28": post26_status,
        "www_authenticate": www[:400],
        "resource_metadata": meta,
        "hint": None
        if post_ok
        else "Need POST /mcp HTTP 401 plus WWW-Authenticate: Bearer ... resource_metadata=<absolute https url>, or HTTP 200 JSON-RPC initialize/discover (MCP 2026-07-28 anonymous discovery).",
    }
    if not post_ok:
        report["ok"] = False
    elif mode == "anonymous_discovery_2026-07-28":
        report["warnings"].append(
            "Anonymous discovery on 2026-07-28: older clients only start OAuth on a first-POST 401. A version gate (401 for old protocolVersion, 200 for 2026-07-28) covers both."
        )

    if meta:
        abs_ok = _is_absolute_https(meta)
        abs_source = "www-authenticate"
    elif anon_ok and prm_any:
        abs_ok = True
        abs_source = "well-known"
        meta = (prm_origin.get("url") if prm_origin.get("ok") else None) or (
            prm_path.get("url") if prm_path.get("ok") else None
        )
    else:
        abs_ok = False
        abs_source = None
    report["checks"]["resource_metadata_absolute"] = {
        "ok": abs_ok,
        "resource_metadata": meta,
        "source": abs_source,
        "hint": None
        if abs_ok
        else "resource_metadata must be an absolute HTTPS URL on the 401 WWW-Authenticate header, or RFC 9728 JSON at origin /.well-known/oauth-protected-resource when using anonymous discovery.",
    }
    if not abs_ok:
        report["ok"] = False

    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Diagnose MCP OAuth for claude.ai / Cursor / Grok")
    p.add_argument("url", help="Public HTTPS origin or /mcp URL")
    args = p.parse_args(argv)
    report = diagnose(args.url)
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
