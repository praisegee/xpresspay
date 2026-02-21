"""Payment resource — initialize and verify transactions."""

from __future__ import annotations

from .._http import HttpClient
from ..models import (
    InitializeRequest,
    InitializeResponse,
    VerifyRequest,
    VerifyResponse,
)


class PaymentResource:
    def __init__(self, http: HttpClient, base_url: str) -> None:
        self._http = http
        self._base_url = base_url

    def initialize(self, request: InitializeRequest) -> InitializeResponse:
        """Initialize a payment transaction and return a hosted payment URL."""
        raw = self._http.post(
            f"{self._base_url}/api/Payments/Initialize",
            request.to_dict(),
        )
        data = raw.get("data") or {}
        return InitializeResponse(
            response_code=raw.get("responseCode", ""),
            response_message=raw.get("responseMessage", ""),
            payment_url=data.get("paymentUrl"),
            reference=data.get("reference"),
            raw=raw,
        )

    def verify(self, request: VerifyRequest) -> VerifyResponse:
        """Verify the status of a transaction by its transaction ID."""
        raw = self._http.post(
            f"{self._base_url}/api/Payments/VerifyPayment",
            request.to_dict(),
        )
        return VerifyResponse(
            response_code=raw.get("responseCode", ""),
            response_message=raw.get("responseMessage", ""),
            raw=raw,
        )
