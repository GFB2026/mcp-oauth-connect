import os
from unittest import mock

from template.oauth_policy import load_allowlist, redirect_uri_allowed


def test_claude_https_callbacks_allowed():
    allow = load_allowlist()
    assert redirect_uri_allowed("https://claude.ai/api/mcp/auth_callback", allow)
    assert redirect_uri_allowed("https://claude.com/api/mcp/auth_callback", allow)


def test_cursor_plugin_loopback_exact():
    allow = load_allowlist()
    assert redirect_uri_allowed("http://localhost:8787/callback", allow)
    assert redirect_uri_allowed("http://127.0.0.1:8787/callback", allow)


def test_attacker_callback_rejected():
    allow = load_allowlist()
    assert not redirect_uri_allowed("https://evil.example/callback", allow)
    assert not redirect_uri_allowed("http://evil.example/callback", allow)


def test_wrong_cursor_port_rejected_when_not_grok_loopback():
    allow = load_allowlist()
    # 9999 is not in the default allowlist. Grok loopback would still accept
    # http://127.0.0.1:9999/callback when MCP_ALLOW_LOOPBACK=1.
    with mock.patch.dict(os.environ, {"MCP_ALLOW_LOOPBACK": "0"}, clear=False):
        # re-import behavior uses env at call time
        from template import oauth_policy as p

        assert not p.redirect_uri_allowed("http://localhost:9999/callback", allow)


def test_grok_ephemeral_loopback_when_enabled():
    with mock.patch.dict(os.environ, {"MCP_ALLOW_LOOPBACK": "1"}, clear=False):
        from template import oauth_policy as p

        assert p.redirect_uri_allowed("http://127.0.0.1:54321/callback")


def test_path_must_be_callback():
    with mock.patch.dict(os.environ, {"MCP_ALLOW_LOOPBACK": "1"}, clear=False):
        from template import oauth_policy as p

        assert not p.redirect_uri_allowed("http://127.0.0.1:54321/oauth/callback")
