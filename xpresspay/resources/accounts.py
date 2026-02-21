"""
Bank account payment resource.

Covers the full Xpresspay direct debit (account) payment lifecycle:
  1. Initiate  — encrypt account data and POST to /v1/payments
  2. Validate OTP — submit the OTP received by the account holder
  3. Query — verify the final status
"""

from __future__ import annotations

from typing import Any

from .._http import HttpClient
from ..encryption import encrypt_payload
from ..models import (
    AccountPaymentRequest,
    OtpValidationRequest,
    PaymentQueryRequest,
    PaymentResponse,
)


class AccountResource:
    """Manages direct bank account debit payment operations."""

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

    def initiate(self, request: AccountPaymentRequest) -> PaymentResponse:
        """
        Encrypt bank account details and initiate a direct debit payment.

        After a successful initiation the customer receives an OTP on their
        registered mobile number. Pass it to :meth:`validate_otp`.

        Bank-specific requirements:
        - **Zenith / UBA**: ``request.date_of_birth`` must be set (DDMMYYYY).
        - **UBA**: ``request.bvn`` must be set.
        - **GTB / First Bank**: ``request.redirect_url`` must be set.

        Args:
            request: An :class:`~xpresspay.models.AccountPaymentRequest`.

        Returns:
            :class:`~xpresspay.models.PaymentResponse`
        """
        encrypted = encrypt_payload(request.to_encrypt_dict(), self._secret_key)
        body: dict[str, Any] = {
            "publicKey": self._public_key,
            "request": encrypted,
            "alg": "3DES-24",
            "paymentType": "ACCOUNT",
        }
        raw = self._http.post(f"{self._base}/v1/payments", body)
        return PaymentResponse(
            status=raw.get("status", ""),
            message=raw.get("message", ""),
            raw=raw,
        )

    # ------------------------------------------------------------------
    # Step 2 – Validate OTP
    # ------------------------------------------------------------------

    def validate_otp(self, request: OtpValidationRequest) -> PaymentResponse:
        """
        Submit the OTP sent to the account holder to authorise the debit.

        Args:
            request: An :class:`~xpresspay.models.OtpValidationRequest` with
                ``payment_type="ACCOUNT"``.

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
    # Step 3 – Query / verify
    # ------------------------------------------------------------------

    def query(self, request: PaymentQueryRequest) -> PaymentResponse:
        """
        Query the final status of a bank account payment.

        Always verify ``response.is_successful`` and that ``response.amount``
        matches your order total before fulfilling the transaction.

        Args:
            request: A :class:`~xpresspay.models.PaymentQueryRequest` with
                ``payment_type="ACCOUNT"``.

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
