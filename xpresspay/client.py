"""
XpressPay client — the primary entry point for the SDK.

Usage::

    import os
    from xpresspay import XpressPay

    client = XpressPay(
        public_key=os.environ["XPRESSPAY_PUBLIC_KEY"],
        secret_key=os.environ["XPRESSPAY_SECRET_KEY"],
        sandbox=True,   # set False for production
    )

    # Card payment
    from xpresspay.models import CardPaymentRequest

    response = client.cards.initiate(
        CardPaymentRequest(
            public_key=client.public_key,
            card_number="5438898014560229",
            cvv="789",
            expiry_month="09",
            expiry_year="25",
            amount="5000",
            email="customer@example.com",
            transaction_id="ORDER-001",
        )
    )

    if response.suggested_authentication == "PIN":
        # Ask customer for their card PIN, then:
        from xpresspay.models import CardPinAuthRequest
        auth_response = client.cards.authenticate_pin(
            CardPinAuthRequest(
                public_key=client.public_key,
                transaction_id="ORDER-001",
                pin="1234",
            )
        )
"""

from __future__ import annotations

import httpx

from ._http import HttpClient
from .resources.accounts import AccountResource
from .resources.banks import BanksResource
from .resources.cards import CardResource

_LIVE_BASE_URL = "https://api.xpresspayonline.com"
_SANDBOX_BASE_URL = "https://xpresspayonlineapisandbox.xpresspayments.com"


class XpressPay:
    """
    Synchronous Xpresspay API client.

    Args:
        public_key: Your Xpresspay public key (``XPPUBK-...``).
            Can be included in client-side code; only creates transactions.
        secret_key: Your Xpresspay secret key (``XPSECK-...``).
            **Keep this server-side only.** It is used solely for local
            encryption and never transmitted over the network.
        sandbox: When ``True`` (default) requests are sent to the sandbox
            environment. Set to ``False`` for live/production.
        timeout: Request timeout in seconds (default: 30).

    Attributes:
        cards: :class:`~xpresspay.resources.cards.CardResource`
        accounts: :class:`~xpresspay.resources.accounts.AccountResource`
        banks: :class:`~xpresspay.resources.banks.BanksResource`
    """

    def __init__(
        self,
        public_key: str,
        secret_key: str,
        *,
        sandbox: bool = True,
        timeout: float = 30.0,
    ) -> None:
        if not public_key or not public_key.startswith("XPPUBK-"):
            raise ValueError(
                "public_key must be a valid Xpresspay public key "
                "starting with 'XPPUBK-'."
            )
        if not secret_key or not secret_key.startswith("XPSECK-"):
            raise ValueError(
                "secret_key must be a valid Xpresspay secret key "
                "starting with 'XPSECK-'."
            )

        self._public_key = public_key
        # Store secret_key privately; never expose it in __repr__ or logs
        self.__secret_key = secret_key
        self._sandbox = sandbox
        self._base_url = _SANDBOX_BASE_URL if sandbox else _LIVE_BASE_URL

        self._http = HttpClient(
            timeout=httpx.Timeout(timeout, connect=10.0),
        )

        self.cards = CardResource(
            public_key=public_key,
            secret_key=self.__secret_key,
            http=self._http,
            base_url=self._base_url,
        )
        self.accounts = AccountResource(
            public_key=public_key,
            secret_key=self.__secret_key,
            http=self._http,
            base_url=self._base_url,
        )
        self.banks = BanksResource(
            public_key=public_key,
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
        # Deliberately omit secret key from repr
        return f"XpressPay(public_key={self._public_key!r}, mode={mode!r})"
