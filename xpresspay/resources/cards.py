"""
Card payment resource.

Covers the full Xpresspay card payment lifecycle:
  1. Initiate  — encrypt card data and POST to /v1/payments
  2. Authenticate — submit PIN or billing address (AVS) to /v1/payments/authenticate
  3. Validate OTP — submit the OTP received by the customer to /v1/payments/validate
  4. Query — verify the final status at /v1/payments/query
"""

from __future__ import annotations

from typing import Any

from .._http import HttpClient
from ..encryption import encrypt_payload
from ..models import (
    CardAvsAuthRequest,
    CardPaymentRequest,
    CardPinAuthRequest,
    OtpValidationRequest,
    PaymentQueryRequest,
    PaymentResponse,
)


class CardResource:
    """Manages all card-based payment operations."""

    def __init__(
        self,
        public_key: str,
        secret_key: str,
        http: HttpClient,
        base_url: str,
    ) -> None:
        self._public_key = public_key
        self._secret_key = secret_key
        self._http = http
        self._base = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Step 1 – Initiate
    # ------------------------------------------------------------------

    def initiate(self, request: CardPaymentRequest) -> PaymentResponse:
        """
        Encrypt card details and initiate a payment.

        Inspect the returned ``PaymentResponse`` to determine the next step:

        - ``suggested_authentication == 'PIN'`` → call :meth:`authenticate_pin`
        - ``suggested_authentication == 'AVS_VBVSECURECODE'`` → call
          :meth:`authenticate_avs`
        - ``is_successful`` → payment settled (rare on first call)

        Args:
            request: A :class:`~xpresspay.models.CardPaymentRequest` instance.

        Returns:
            :class:`~xpresspay.models.PaymentResponse`
        """
        encrypted = encrypt_payload(request.to_encrypt_dict(), self._secret_key)
        body: dict[str, Any] = {
            "publicKey": self._public_key,
            "request": encrypted,
            "alg": "3DES-24",
            "paymentType": "CARD",
        }
        raw = self._http.post(f"{self._base}/v1/payments", body)
        return PaymentResponse(
            status=raw.get("status", ""),
            message=raw.get("message", ""),
            raw=raw,
        )

    # ------------------------------------------------------------------
    # Step 2a – Authenticate with PIN (Nigerian cards)
    # ------------------------------------------------------------------

    def authenticate_pin(self, request: CardPinAuthRequest) -> PaymentResponse:
        """
        Submit a cardholder PIN for local (Nigerian) cards.

        After this, the customer typically receives an OTP; call
        :meth:`validate_otp` next.

        Args:
            request: A :class:`~xpresspay.models.CardPinAuthRequest` instance.

        Returns:
            :class:`~xpresspay.models.PaymentResponse`
        """
        raw = self._http.post(
            f"{self._base}/v1/payments/authenticate", request.to_dict()
        )
        return PaymentResponse(
            status=raw.get("status", ""),
            message=raw.get("message", ""),
            raw=raw,
        )

    # ------------------------------------------------------------------
    # Step 2b – Authenticate with AVS (international cards)
    # ------------------------------------------------------------------

    def authenticate_avs(self, request: CardAvsAuthRequest) -> PaymentResponse:
        """
        Submit billing address for AVS / 3DSecure international cards.

        If the response contains an ``auth_url``, render it in an iframe so
        the cardholder can complete 3DSecure authentication.

        Args:
            request: A :class:`~xpresspay.models.CardAvsAuthRequest` instance.

        Returns:
            :class:`~xpresspay.models.PaymentResponse`
        """
        raw = self._http.post(
            f"{self._base}/v1/payments/authenticate", request.to_dict()
        )
        return PaymentResponse(
            status=raw.get("status", ""),
            message=raw.get("message", ""),
            raw=raw,
        )

    # ------------------------------------------------------------------
    # Step 3 – Validate OTP
    # ------------------------------------------------------------------

    def validate_otp(self, request: OtpValidationRequest) -> PaymentResponse:
        """
        Submit the OTP received by the customer to complete authentication.

        Args:
            request: A :class:`~xpresspay.models.OtpValidationRequest` with
                ``payment_type="CARD"``.

        Returns:
            :class:`~xpresspay.models.PaymentResponse`
        """
        raw = self._http.post(
            f"{self._base}/v1/payments/validate", request.to_dict()
        )
        return PaymentResponse(
            status=raw.get("status", ""),
            message=raw.get("message", ""),
            raw=raw,
        )

    # ------------------------------------------------------------------
    # Step 4 – Query / verify
    # ------------------------------------------------------------------

    def query(self, request: PaymentQueryRequest) -> PaymentResponse:
        """
        Query the final status of a card payment.

        Always call this server-side after the customer's browser returns from
        a redirect or after receiving a webhook — never trust the client alone.

        Check ``response.is_successful`` and verify ``response.amount`` matches
        your order total before delivering value.

        Args:
            request: A :class:`~xpresspay.models.PaymentQueryRequest` with
                ``payment_type="CARD"``.

        Returns:
            :class:`~xpresspay.models.PaymentResponse`
        """
        raw = self._http.post(
            f"{self._base}/v1/payments/query", request.to_dict()
        )
        return PaymentResponse(
            status=raw.get("status", ""),
            message=raw.get("message", ""),
            raw=raw,
        )
