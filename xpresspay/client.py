"""
XpressPay client — the primary entry point for the SDK.

Usage::

    from xpresspay import XpressPay

    # Reads XPRESSPAY_PUBLIC_KEY from the environment automatically
    client = XpressPay(sandbox=True)

    # Or pass the key explicitly
    client = XpressPay(public_key="XPPUBK-...", sandbox=True)

    from xpresspay.models import InitializeRequest

    response = client.payments.initialize(
        InitializeRequest(
            amount="1000.00",
            email="customer@example.com",
            transaction_id="ORDER-001",
        )
    )

    if response.is_successful:
        # Redirect customer to response.payment_url
        print(response.payment_url)
"""

from __future__ import annotations

import os

import httpx

from ._http import HttpClient
from .resources.payments import PaymentResource

_LIVE_BASE_URL = "https://myxpresspay.com:6004"
_SANDBOX_BASE_URL = "https://pgsandbox.xpresspayments.com:6004"


class XpressPay:
    """
    Synchronous Xpresspay API client.

    Args:
        public_key: Your Xpresspay public key (``XPPUBK-...``).
            If omitted, the value of the ``XPRESSPAY_PUBLIC_KEY`` environment
            variable is used.
        sandbox: When ``True`` (default) requests are sent to the sandbox
            environment. Set to ``False`` for live/production.
        timeout: Request timeout in seconds (default: 30).

    Attributes:
        payments: :class:`~xpresspay.resources.payments.PaymentResource`
    """

    def __init__(
        self,
        public_key: str | None = None,
        *,
        sandbox: bool = True,
        timeout: float = 30.0,
    ) -> None:
        resolved_key = public_key or os.environ.get("XPRESSPAY_PUBLIC_KEY", "")

        if not resolved_key or not resolved_key.startswith("XPPUBK-"):
            raise ValueError(
                "A valid Xpresspay public key starting with 'XPPUBK-' is required. "
                "Pass it as public_key or set the XPRESSPAY_PUBLIC_KEY "
                "environment variable."
            )

        self._public_key = resolved_key
        self._sandbox = sandbox
        self._base_url = _SANDBOX_BASE_URL if sandbox else _LIVE_BASE_URL

        self._http = HttpClient(
            public_key=self._public_key,
            timeout=httpx.Timeout(timeout, connect=10.0),
        )

        self.payments = PaymentResource(
            http=self._http,
            base_url=self._base_url,
        )

    @property
    def public_key(self) -> str:
        """The configured public key."""
        return self._public_key

    @property
    def is_sandbox(self) -> bool:
        """``True`` when pointing at the sandbox environment."""
        return self._sandbox

    def close(self) -> None:
        """Release underlying HTTP connections."""
        self._http.close()

    def __enter__(self) -> XpressPay:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __repr__(self) -> str:
        mode = "sandbox" if self._sandbox else "live"
        return f"XpressPay(public_key={self._public_key!r}, mode={mode!r})"
