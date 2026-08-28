"""Allowlist-gated OAuth provider for public MCP servers.

SECURITY: allowlist DCR closed attacker callbacks, not consent. Auto-approve
still mints a code to any client that hits /register + /authorize with an
allowlisted redirect. Ping-only is acceptable. Host tools are not — read
template/README.md before wiring shell, mail, or files.

claude.ai / Claude Desktop / Cursor / Grok use RFC 7591 dynamic client
registration. There is no stable official client_id. The stable value is the
redirect_uri each host posts the auth code back to. Register and authorize
only those URIs.

Modes (env MCP_DCR_MODE):
  allowlist (default) — DCR on; reject unknown redirect_uris.
  disabled — DCR refused; seed one static client from MCP_STATIC_CLIENT_*.

Clients, access tokens, and refresh tokens persist to JSON. Auth codes stay
in memory (5-minute expiry). Persistence uses pydantic model_dump(mode="json")
so AnyUrl fields serialize as strings (json.dump of __dict__ truncates the file).

Compatible with mcp 1.27 OAuthAuthorizationServerProvider (plural scopes,
object revoke_token).
"""

from __future__ import annotations

import json
import logging
import os
import secrets
import time
from pathlib import Path

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    OAuthAuthorizationServerProvider,
    OAuthClientInformationFull,
    OAuthToken,
    RefreshToken,
    RegistrationError,
    TokenError,
    construct_redirect_uri,
)

from oauth_policy import is_grok_loopback_redirect, load_allowlist, redirect_uri_allowed

logger = logging.getLogger(__name__)

_DEFAULT_PERSIST_PATH = Path(__file__).parent / "oauth_state.json"

_ACCESS_TTL_HTTPS = int(os.environ.get("MCP_ACCESS_TTL_HTTPS", str(7 * 86400)))
_REFRESH_TTL_HTTPS = int(os.environ.get("MCP_REFRESH_TTL_HTTPS", str(30 * 86400)))
_ACCESS_TTL_LOOPBACK = int(os.environ.get("MCP_ACCESS_TTL_LOOPBACK", str(4 * 3600)))
_REFRESH_TTL_LOOPBACK = int(os.environ.get("MCP_REFRESH_TTL_LOOPBACK", str(2 * 86400)))


def _is_loopback_client(client: OAuthClientInformationFull) -> bool:
    uris = [str(u) for u in (client.redirect_uris or [])]
    return bool(uris) and all(is_grok_loopback_redirect(u) for u in uris)


def _ttls_for_client(client: OAuthClientInformationFull) -> tuple[int, int]:
    if _is_loopback_client(client):
        return _ACCESS_TTL_LOOPBACK, _REFRESH_TTL_LOOPBACK
    return _ACCESS_TTL_HTTPS, _REFRESH_TTL_HTTPS


class AllowlistOAuthProvider(OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]):
    def __init__(self, persist_path: Path | str | None = None):
        self.persist_path = Path(persist_path) if persist_path else _DEFAULT_PERSIST_PATH
        self.clients: dict[str, OAuthClientInformationFull] = {}
        self.auth_codes: dict[str, AuthorizationCode] = {}
        self.access_tokens: dict[str, AccessToken] = {}
        self.refresh_tokens: dict[str, RefreshToken] = {}
        self.mode = os.environ.get("MCP_DCR_MODE", "allowlist").strip().lower()
        self.allowed_redirects = load_allowlist()
        self.pinned_client_id = os.environ.get("MCP_ALLOWED_CLIENT_ID", "").strip() or None
        self._load()
        if self.mode == "disabled":
            self._seed_static_client()
        logger.info(
            "OAuth provider policy: mode=%s, allowed_redirects=%s, pinned_client_id=%s",
            self.mode,
            self.allowed_redirects,
            "set" if self.pinned_client_id else "none",
        )

    def _seed_static_client(self) -> None:
        cid = os.environ.get("MCP_STATIC_CLIENT_ID", "").strip()
        secret = os.environ.get("MCP_STATIC_CLIENT_SECRET", "").strip()
        redirect = os.environ.get("MCP_STATIC_REDIRECT_URI", "").strip()
        if not (cid and redirect):
            logger.warning("MCP_DCR_MODE=disabled but static client env unset")
            return
        self.clients[cid] = OAuthClientInformationFull(
            client_id=cid,
            client_secret=secret or None,
            redirect_uris=[redirect],
            grant_types=["authorization_code", "refresh_token"],
            token_endpoint_auth_method="client_secret_post" if secret else "none",
        )

    def _load(self) -> None:
        if not self.persist_path.exists():
            return
        try:
            with open(self.persist_path, encoding="utf-8") as f:
                data = json.load(f)
            self.clients = {
                cid: OAuthClientInformationFull(**client) for cid, client in data.get("clients", {}).items()
            }
            self.access_tokens = {token: AccessToken(**at) for token, at in data.get("access_tokens", {}).items()}
            self.refresh_tokens = {token: RefreshToken(**rt) for token, rt in data.get("refresh_tokens", {}).items()}
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as e:
            logger.error("Failed to load OAuth state: %s", e)

    def _save(self) -> None:
        data = {
            "clients": {cid: client.model_dump(mode="json") for cid, client in self.clients.items()},
            "access_tokens": {token: at.model_dump(mode="json") for token, at in self.access_tokens.items()},
            "refresh_tokens": {token: rt.model_dump(mode="json") for token, rt in self.refresh_tokens.items()},
        }
        try:
            tmp = self.persist_path.with_suffix(self.persist_path.suffix + ".tmp")
            fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as f:
                json.dump(data, f)
            os.chmod(tmp, 0o600)
            os.replace(tmp, self.persist_path)
        except OSError as e:
            logger.error("Failed to save OAuth state: %s", e)

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self.clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        if self.mode == "disabled":
            raise RegistrationError(
                error="invalid_client_metadata",
                error_description="Dynamic client registration is disabled on this server.",
            )
        redirect_uris = [str(uri) for uri in (client_info.redirect_uris or [])]
        if not redirect_uris:
            raise RegistrationError(
                error="invalid_redirect_uri",
                error_description="At least one redirect_uri is required.",
            )
        for uri in redirect_uris:
            if not redirect_uri_allowed(uri, self.allowed_redirects):
                logger.warning("Rejected client registration for redirect_uri=%s", uri)
                raise RegistrationError(
                    error="invalid_redirect_uri",
                    error_description=f"redirect_uri '{uri}' is not in the allowlist.",
                )
        client_id = secrets.token_hex(16)
        client_info.client_id = client_id
        # Public clients (claude.ai: token_endpoint_auth_method=none + PKCE)
        # must not get a secret — mcp then 401s the token exchange.
        if client_info.token_endpoint_auth_method in ("client_secret_post", "client_secret_basic"):
            client_info.client_secret = secrets.token_hex(32)
        else:
            client_info.client_secret = None
            client_info.token_endpoint_auth_method = "none"
        client_info.client_id_issued_at = int(time.time())
        self.clients[client_id] = client_info
        self._save()
        logger.info(
            "Registered OAuth client %s (auth_method=%s, redirect_uris=%s)",
            client_id,
            client_info.token_endpoint_auth_method,
            redirect_uris,
        )

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        if self.pinned_client_id and client.client_id != self.pinned_client_id:
            raise AuthorizeError(
                error="access_denied",
                error_description="This client is not authorized on this server.",
            )
        if not redirect_uri_allowed(str(params.redirect_uri), self.allowed_redirects):
            logger.warning(
                "Rejected authorize for client=%s redirect_uri=%s",
                client.client_id,
                params.redirect_uri,
            )
            raise AuthorizeError(
                error="invalid_request",
                error_description="redirect_uri is not in the allowlist.",
            )
        code = secrets.token_hex(32)
        self.auth_codes[code] = AuthorizationCode(
            code=code,
            scopes=params.scopes or [],
            expires_at=time.time() + 300,
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
        )
        return construct_redirect_uri(str(params.redirect_uri), code=code, state=params.state)

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        auth_code = self.auth_codes.get(authorization_code)
        if not auth_code or auth_code.client_id != client.client_id:
            return None
        if auth_code.expires_at < time.time():
            self.auth_codes.pop(authorization_code, None)
            return None
        return auth_code

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        auth_code = self.auth_codes.pop(authorization_code.code, None)
        if not auth_code or auth_code.expires_at < time.time():
            raise TokenError(error="invalid_grant", error_description="Invalid or expired authorization code")
        scopes = list(auth_code.scopes or [])
        access_token = secrets.token_hex(32)
        refresh_token = secrets.token_hex(32)
        expires_in, refresh_ttl = _ttls_for_client(client)
        now = int(time.time())
        self.access_tokens[access_token] = AccessToken(
            token=access_token,
            client_id=client.client_id,
            scopes=scopes,
            expires_at=now + expires_in,
            resource=auth_code.resource,
        )
        self.refresh_tokens[refresh_token] = RefreshToken(
            token=refresh_token,
            client_id=client.client_id,
            scopes=scopes,
            expires_at=now + refresh_ttl,
        )
        self._save()
        return OAuthToken(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            refresh_token=refresh_token,
            scope=" ".join(scopes) if scopes else None,
        )

    async def load_refresh_token(self, client: OAuthClientInformationFull, refresh_token: str) -> RefreshToken | None:
        ref_token = self.refresh_tokens.get(refresh_token)
        if not ref_token or ref_token.client_id != client.client_id:
            return None
        if ref_token.expires_at is None or ref_token.expires_at < time.time():
            self.refresh_tokens.pop(refresh_token, None)
            self._save()
            return None
        return ref_token

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        ref_token = self.refresh_tokens.get(refresh_token.token)
        if not ref_token:
            raise TokenError(error="invalid_grant", error_description="Invalid refresh token")
        granted = list(ref_token.scopes or [])
        if scopes:
            if not set(scopes).issubset(set(granted)):
                raise TokenError(
                    error="invalid_scope",
                    error_description="Requested scopes exceed the originally granted scopes.",
                )
            granted = list(scopes)
        access_token = secrets.token_hex(32)
        new_refresh_token = secrets.token_hex(32)
        expires_in, refresh_ttl = _ttls_for_client(client)
        now = int(time.time())
        self.access_tokens[access_token] = AccessToken(
            token=access_token,
            client_id=client.client_id,
            scopes=granted,
            expires_at=now + expires_in,
            resource=getattr(refresh_token, "resource", None) or getattr(ref_token, "resource", None),
        )
        self.refresh_tokens[new_refresh_token] = RefreshToken(
            token=new_refresh_token,
            client_id=client.client_id,
            scopes=granted,
            expires_at=now + refresh_ttl,
        )
        self.refresh_tokens.pop(refresh_token.token, None)
        self._save()
        return OAuthToken(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            refresh_token=new_refresh_token,
            scope=" ".join(granted) if granted else None,
        )

    async def load_access_token(self, token: str) -> AccessToken | None:
        access = self.access_tokens.get(token)
        if not access:
            return None
        if access.expires_at is not None and access.expires_at < time.time():
            self.access_tokens.pop(token, None)
            self._save()
            return None
        return access

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        key = getattr(token, "token", None)
        if not key:
            return
        self.access_tokens.pop(key, None)
        self.refresh_tokens.pop(key, None)
        self._save()
