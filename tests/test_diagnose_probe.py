import json
from unittest import mock

import diagnose as diagnose_mod


def _http(status, headers, body):
    return status, {k.lower(): v for k, v in headers.items()}, body


def test_https_required():
    r = diagnose_mod.diagnose("http://example.com")
    assert r["ok"] is False
    assert "https" in r["error"]


def test_pass_when_as_and_401_www():
    as_body = json.dumps(
        {
            "issuer": "https://mcp.example.com",
            "authorization_endpoint": "https://mcp.example.com/authorize",
            "token_endpoint": "https://mcp.example.com/token",
            "registration_endpoint": "https://mcp.example.com/register",
        }
    ).encode()
    www = 'Bearer error="invalid_token", resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"'

    def fake_get(url, timeout=12.0):
        if url.endswith("oauth-authorization-server"):
            return _http(200, {}, as_body)
        return _http(401, {"WWW-Authenticate": www}, b"")

    with mock.patch.object(diagnose_mod, "_get", side_effect=fake_get):
        r = diagnose_mod.diagnose("https://mcp.example.com")
    assert r["ok"] is True


def test_fail_when_mcp_returns_200():
    as_body = json.dumps(
        {
            "issuer": "https://mcp.example.com",
            "authorization_endpoint": "https://mcp.example.com/authorize",
            "token_endpoint": "https://mcp.example.com/token",
            "registration_endpoint": "https://mcp.example.com/register",
        }
    ).encode()

    def fake_get(url, timeout=12.0):
        if url.endswith("oauth-authorization-server"):
            return _http(200, {}, as_body)
        return _http(200, {}, b'{"jsonrpc":"2.0"}')

    with mock.patch.object(diagnose_mod, "_get", side_effect=fake_get):
        r = diagnose_mod.diagnose("https://mcp.example.com")
    assert r["ok"] is False
    assert r["checks"]["unauthenticated_mcp"]["ok"] is False
