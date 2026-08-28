import os
from unittest import mock

from license.check import require_license, verify_key
from license.issue import main as issue_main


def test_dev_skips():
    with mock.patch.dict(os.environ, {"MCP_OAUTH_DEV": "1"}, clear=False):
        require_license()


def test_issue_and_verify():
    secret = "test-secret-not-for-prod"
    with mock.patch.dict(os.environ, {"MCP_OAUTH_LICENSE_SECRET": secret}):
        # capture print
        import io
        import sys

        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = issue_main(["issue.py", "buyer@example.com", "0"])
        finally:
            sys.stdout = old
        assert rc == 0
        key = buf.getvalue().strip()
    ok, reason = verify_key(key, secret)
    assert ok, reason
