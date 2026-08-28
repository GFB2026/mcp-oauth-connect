import json
from unittest import mock

import diagnose as diagnose_mod

AS_BODY = json.dumps(
    {
        "issuer": "https://mcp.example.com",
        "authorization_endpoint": "https://mcp.example.com/authorize",
        "token_endpoint": "https://mcp.example.com/token",
        "registration_endpoint": "https://mcp.example.com/register",
        "code_challenge_methods_supported": ["S256"],
    }
).encode()

PRM_BODY = json.dumps(
    {
        "resource": "https://mcp.example.com/mcp",
        "authorization_servers": ["https://mcp.example.com"],
    }
).encode()

WWW = (
    'Bearer error="invalid_token", '
    'resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource/mcp"'
)


def _http(status, headers=None, body=b"", location=None):
    return status, {k.lower(): v for k, v in (headers or {}).items()}, body, location


def _router(as_body=AS_BODY, prm_origin=None, prm_path=PRM_BODY, get_mcp=None, post_mcp=None):
    def fake_request(method, url, data=None, timeout=12.0, content_type=None):
        if url.endswith("oauth-authorization-server") or url.endswith("openid-configuration"):
            return _http(200, {}, as_body)
        if url.endswith("oauth-protected-resource/mcp"):
            if prm_path is None:
                return _http(404, {}, b"Not Found")
            return _http(200, {"Content-Type": "application/json"}, prm_path)
        if url.endswith("oauth-protected-resource"):
            if prm_origin is None:
                return _http(404, {}, b"Not Found")
            return _http(200, {"Content-Type": "application/json"}, prm_origin)
        if method == "POST":
            return post_mcp or _http(401, {"WWW-Authenticate": WWW}, b"{}")
        return get_mcp or _http(401, {"WWW-Authenticate": WWW}, b"{}")

    return fake_request


def test_https_required():
    r = diagnose_mod.diagnose("http://example.com")
    assert r["ok"] is False
    assert "https" in r["error"]


def test_pass_live_shaped_path_prm_get_and_post_401():
    with mock.patch.object(diagnose_mod, "_request", side_effect=_router()):
        r = diagnose_mod.diagnose("https://mcp.example.com")
    assert r["ok"] is True
    assert r["checks"]["code_challenge_s256"]["ok"] is True
    assert r["checks"]["protected_resource_metadata"]["ok"] is False
    assert r["checks"]["protected_resource_metadata_path"]["ok"] is True
    assert r["checks"]["protected_resource_metadata_any"]["ok"] is True
    assert r["checks"]["unauthenticated_mcp_get"]["ok"] is True
    assert r["checks"]["unauthenticated_mcp_post"]["ok"] is True
    assert r["checks"]["resource_metadata_absolute"]["ok"] is True


def test_pass_when_get_is_405_and_post_401():
    with mock.patch.object(
        diagnose_mod,
        "_request",
        side_effect=_router(get_mcp=_http(405, {}, b"")),
    ):
        r = diagnose_mod.diagnose("https://mcp.example.com/mcp")
    assert r["ok"] is True
    assert r["checks"]["unauthenticated_mcp_get"]["status"] == 405


def test_fail_when_mcp_get_returns_200():
    with mock.patch.object(
        diagnose_mod,
        "_request",
        side_effect=_router(get_mcp=_http(200, {}, b'{"jsonrpc":"2.0"}')),
    ):
        r = diagnose_mod.diagnose("https://mcp.example.com")
    assert r["ok"] is False
    assert r["checks"]["unauthenticated_mcp_get"]["ok"] is False


def test_fail_relative_resource_metadata():
    www = 'Bearer resource_metadata="/.well-known/oauth-protected-resource"'
    with mock.patch.object(
        diagnose_mod,
        "_request",
        side_effect=_router(
            get_mcp=_http(401, {"WWW-Authenticate": www}, b""),
            post_mcp=_http(401, {"WWW-Authenticate": www}, b""),
        ),
    ):
        r = diagnose_mod.diagnose("https://mcp.example.com")
    assert r["ok"] is False
    assert r["checks"]["resource_metadata_absolute"]["ok"] is False


def test_fail_missing_s256():
    as_body = json.dumps(
        {
            "issuer": "https://mcp.example.com",
            "authorization_endpoint": "https://mcp.example.com/authorize",
            "token_endpoint": "https://mcp.example.com/token",
            "registration_endpoint": "https://mcp.example.com/register",
        }
    ).encode()
    with mock.patch.object(diagnose_mod, "_request", side_effect=_router(as_body=as_body)):
        r = diagnose_mod.diagnose("https://mcp.example.com")
    assert r["ok"] is False
    assert r["checks"]["code_challenge_s256"]["ok"] is False


def test_fail_cross_host_redirect():
    with mock.patch.object(
        diagnose_mod,
        "_request",
        side_effect=_router(
            get_mcp=_http(301, {}, b"", location="https://other.example/mcp"),
        ),
    ):
        r = diagnose_mod.diagnose("https://mcp.example.com")
    assert r["ok"] is False
    assert r["checks"]["mcp_no_cross_host_redirect"]["ok"] is False


def test_fail_when_both_prm_missing():
    with mock.patch.object(
        diagnose_mod,
        "_request",
        side_effect=_router(prm_origin=None, prm_path=None),
    ):
        r = diagnose_mod.diagnose("https://mcp.example.com")
    assert r["ok"] is False
    assert r["checks"]["protected_resource_metadata_any"]["ok"] is False


def test_pass_origin_prm_when_path_missing():
    with mock.patch.object(
        diagnose_mod,
        "_request",
        side_effect=_router(prm_origin=PRM_BODY, prm_path=None),
    ):
        r = diagnose_mod.diagnose("https://mcp.example.com")
    assert r["checks"]["protected_resource_metadata"]["ok"] is True
    assert r["checks"]["protected_resource_metadata_any"]["ok"] is True
    assert r["ok"] is True
