"""
Internal HTTP client wrapper.

Uses ``httpx`` with sane timeouts, Bearer token authentication, and
centralised error mapping from Xpresspay HTTP status codes to SDK exceptions.
"""

from __future__ import annotations

from typing import Any

import httpx

from .exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    ProcessingError,
    ValidationError,
    XpressPayError,
)

_DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


def _raise_for_response(response: httpx.Response) -> None:
    """Map Xpresspay HTTP status codes to typed SDK exceptions."""
    if response.is_success:
        return

    try:
        body: dict[str, Any] = response.json()
    except Exception:
        body = {}

    msg = (
        body.get("responseMessage")
        or body.get("message")
        or response.text
        or "Unknown error"
    )
    err_type = body.get("error", "")

    if response.status_code == 400:
        raise ValidationError(msg, error_type=err_type, status_code=400)
    if response.status_code == 401:
        raise AuthenticationError(msg, status_code=401)
    if response.status_code == 404:
        raise NotFoundError(msg, status_code=404)
    if response.status_code >= 500:
        raise ProcessingError(msg, status_code=response.status_code)

    raise XpressPayError(msg, status_code=response.status_code)


class HttpClient:
    """Thin synchronous wrapper around ``httpx.Client``."""

    def __init__(
        self,
        public_key: str,
        timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
        *,
        verify_ssl: bool = True,
    ) -> None:
        self._client = httpx.Client(
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {public_key}",
            },
            timeout=timeout,
            verify=verify_ssl,
            follow_redirects=True,
        )

    def post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.post(url, json=payload)
        except httpx.TimeoutException as exc:
            raise NetworkError(f"Request timed out: {exc}") from exc
        except httpx.NetworkError as exc:
            raise NetworkError(f"Network error: {exc}") from exc

        _raise_for_response(response)
        return response.json()  # type: ignore[no-any-return]

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
