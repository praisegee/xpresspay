"""
Typed request and response models for the Xpresspay API.

All models use plain dataclasses (no third-party dependency) with
explicit types so editors and type checkers get full coverage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Initialize payment
# ---------------------------------------------------------------------------


@dataclass
class InitializeRequest:
    """
    Fields required to initialize a payment transaction.

    Only ``amount``, ``email``, and ``transaction_id`` are mandatory.
    All other fields are optional.

    ``metadata`` items must be dicts with ``"name"`` and ``"value"`` keys.
    """

    amount: str
    email: str
    transaction_id: str

    currency: str = "NGN"
    product_id: str | None = None
    product_description: str | None = None
    callback_url: str | None = None
    body_color: str | None = None
    button_color: str | None = None
    footer_text: str | None = None
    footer_logo: str | None = None
    split_payment_reference: str | None = None
    is_split_payment: bool = False
    is_api_user: bool = True
    merchant_name: str | None = None
    logo_url: str | None = None
    mode: str | None = None
    apply_conveniency_charge: bool = False
    is_recurring: bool = False
    metadata: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "amount": self.amount,
            "email": self.email,
            "transactionId": self.transaction_id,
            "currency": self.currency,
            "isApiUser": self.is_api_user,
            "isSplitpayment": self.is_split_payment,
            "applyConviniencyCharge": self.apply_conveniency_charge,
            "isRecurring": self.is_recurring,
        }
        if self.product_id:
            payload["productId"] = self.product_id
        if self.product_description:
            payload["productDescription"] = self.product_description
        if self.callback_url:
            payload["callBackUrl"] = self.callback_url
        if self.body_color:
            payload["bodyColor"] = self.body_color
        if self.button_color:
            payload["buttonColor"] = self.button_color
        if self.footer_text:
            payload["footerText"] = self.footer_text
        if self.footer_logo:
            payload["footerLogo"] = self.footer_logo
        if self.split_payment_reference:
            payload["splitPaymentReference"] = self.split_payment_reference
        if self.merchant_name:
            payload["merchantName"] = self.merchant_name
        if self.logo_url:
            payload["logoUrl"] = self.logo_url
        if self.mode:
            payload["mode"] = self.mode
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload


@dataclass
class InitializeResponse:
    """
    Response from the Initialize endpoint.

    ``raw`` always contains the full JSON response for fields not
    covered by the typed attributes.
    """

    response_code: str
    response_message: str
    payment_url: str | None
    reference: str | None
    raw: dict[str, Any]

    @property
    def is_successful(self) -> bool:
        """True when the API accepted and initialized the transaction."""
        return self.response_code == "00"


# ---------------------------------------------------------------------------
# Verify payment
# ---------------------------------------------------------------------------


@dataclass
class VerifyRequest:
    """Fields required to verify a payment transaction."""

    transaction_id: str

    def to_dict(self) -> dict[str, Any]:
        return {"transactionId": self.transaction_id}


@dataclass
class VerifyResponse:
    """
    Response from the VerifyPayment endpoint.

    ``raw`` always contains the full JSON response for fields not
    covered by the typed attributes.
    """

    response_code: str
    response_message: str
    raw: dict[str, Any]

    @property
    def is_successful(self) -> bool:
        """True when the transaction was confirmed as successful."""
        data = self.raw.get("data", {})
        val = data.get("isSuccessful")
        if isinstance(val, bool):
            return val
        return str(val).lower() == "true"

    @property
    def amount(self) -> str | None:
        return self.raw.get("data", {}).get("amount")

    @property
    def currency(self) -> str | None:
        return self.raw.get("data", {}).get("currency")

    @property
    def status(self) -> str | None:
        return self.raw.get("data", {}).get("status")

    @property
    def payment_type(self) -> str | None:
        return self.raw.get("data", {}).get("paymentType")

    @property
    def gateway_response(self) -> str | None:
        return self.raw.get("data", {}).get("gatewayResponse")

    @property
    def transaction_id(self) -> str | None:
        return self.raw.get("data", {}).get("transactionId")
