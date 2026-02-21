"""
Typed request and response models for the Xpresspay API.

All models use plain dataclasses (no third-party dependency) with
explicit types so editors and type checkers get full coverage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Card payment models
# ---------------------------------------------------------------------------


@dataclass
class CardPaymentRequest:
    """
    Fields required to initiate a card payment.

    Only ``public_key``, ``card_number``, ``cvv``, ``expiry_month``,
    ``expiry_year``, ``amount``, ``email``, and ``transaction_id`` are
    mandatory. All other fields are optional but improve auth success rates.
    """

    public_key: str
    card_number: str
    cvv: str
    expiry_month: str
    expiry_year: str
    amount: str
    email: str
    transaction_id: str

    currency: str = "NGN"
    country: str = "NG"
    phone_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    ip: str | None = None
    device_finger_print: str | None = None
    redirect_url: str | None = None

    # Billing address (required for AVS / international cards)
    billing_zip: str | None = None
    billing_city: str | None = None
    billing_address: str | None = None
    billing_state: str | None = None
    billing_country: str | None = None

    # Arbitrary metadata key-value pairs
    meta: list[dict[str, str]] = field(default_factory=list)

    def to_encrypt_dict(self) -> dict[str, Any]:
        """Return the dict that will be JSON-serialised and encrypted."""
        payload: dict[str, Any] = {
            "publicKey": self.public_key,
            "cardNumber": self.card_number,
            "cvv": self.cvv,
            "expiryMonth": self.expiry_month,
            "expiryYear": self.expiry_year,
            "amount": self.amount,
            "email": self.email,
            "transactionId": self.transaction_id,
            "currency": self.currency,
            "country": self.country,
            "paymentType": "CARD",
        }
        if self.phone_number:
            payload["phoneNumber"] = self.phone_number
        if self.first_name:
            payload["firstName"] = self.first_name
        if self.last_name:
            payload["lastName"] = self.last_name
        if self.ip:
            payload["ip"] = self.ip
        if self.device_finger_print:
            payload["deviceFingerPrint"] = self.device_finger_print
        if self.redirect_url:
            payload["redirectUrl"] = self.redirect_url
        if self.billing_zip:
            payload["billingZip"] = self.billing_zip
        if self.billing_city:
            payload["billingCity"] = self.billing_city
        if self.billing_address:
            payload["billingAddress"] = self.billing_address
        if self.billing_state:
            payload["billingState"] = self.billing_state
        if self.billing_country:
            payload["billingCountry"] = self.billing_country
        if self.meta:
            payload["meta"] = self.meta
        return payload


@dataclass
class CardPinAuthRequest:
    """Authenticate a card payment that requires a PIN."""

    public_key: str
    transaction_id: str
    pin: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "publicKey": self.public_key,
            "suggestedAuthentication": "PIN",
            "pin": self.pin,
            "transactionId": self.transaction_id,
            "paymentType": "CARD",
        }


@dataclass
class CardAvsAuthRequest:
    """Authenticate a card payment that requires AVS/3DSecure."""

    public_key: str
    transaction_id: str
    billing_zip: str | None = None
    billing_city: str | None = None
    billing_address: str | None = None
    billing_state: str | None = None
    billing_country: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "publicKey": self.public_key,
            "suggestedAuthentication": "AVS_VBVSECURECODE",
            "transactionId": self.transaction_id,
            "paymentType": "CARD",
        }
        if self.billing_zip:
            payload["billingZip"] = self.billing_zip
        if self.billing_city:
            payload["billingCity"] = self.billing_city
        if self.billing_address:
            payload["billingAddress"] = self.billing_address
        if self.billing_state:
            payload["billingState"] = self.billing_state
        if self.billing_country:
            payload["billingCountry"] = self.billing_country
        return payload


@dataclass
class OtpValidationRequest:
    """Validate a payment OTP (card or bank account)."""

    public_key: str
    transaction_id: str
    otp: str
    payment_type: str  # "CARD" | "ACCOUNT"

    def to_dict(self) -> dict[str, Any]:
        return {
            "publicKey": self.public_key,
            "transactionReference": self.transaction_id,
            "otp": self.otp,
            "paymentType": self.payment_type,
        }


# ---------------------------------------------------------------------------
# Bank account payment models
# ---------------------------------------------------------------------------


@dataclass
class AccountPaymentRequest:
    """
    Fields required to initiate a bank account debit payment.

    ``date_of_birth`` is required for Zenith and UBA banks (format: DDMMYYYY).
    ``bvn`` is required for UBA accounts.
    ``redirect_url`` is required for GTB and First Bank.
    """

    public_key: str
    account_number: str
    bank_code: str
    amount: str
    email: str
    transaction_id: str

    currency: str = "NGN"
    country: str = "NG"
    phone_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    ip: str | None = None
    device_finger_print: str | None = None

    # Bank-specific required fields
    date_of_birth: str | None = None  # DDMMYYYY – Zenith, UBA
    bvn: str | None = None  # UBA
    redirect_url: str | None = None  # GTB, First Bank

    def to_encrypt_dict(self) -> dict[str, Any]:
        """Return the dict that will be JSON-serialised and encrypted."""
        payload: dict[str, Any] = {
            "publicKey": self.public_key,
            "accountNumber": self.account_number,
            "bankCode": self.bank_code,
            "amount": self.amount,
            "email": self.email,
            "transactionId": self.transaction_id,
            "currency": self.currency,
            "country": self.country,
            "paymentType": "ACCOUNT",
        }
        if self.phone_number:
            payload["phoneNumber"] = self.phone_number
        if self.first_name:
            payload["firstName"] = self.first_name
        if self.last_name:
            payload["lastName"] = self.last_name
        if self.ip:
            payload["ip"] = self.ip
        if self.device_finger_print:
            payload["deviceFingerPrint"] = self.device_finger_print
        if self.date_of_birth:
            payload["dateOfBirth"] = self.date_of_birth
        if self.bvn:
            payload["bvn"] = self.bvn
        if self.redirect_url:
            payload["redirectUrl"] = self.redirect_url
        return payload


# ---------------------------------------------------------------------------
# Payment query model
# ---------------------------------------------------------------------------


@dataclass
class PaymentQueryRequest:
    """Query the status of any payment (card or account)."""

    public_key: str
    transaction_id: str
    payment_type: str  # "CARD" | "ACCOUNT" | "QR" | "USSD" | "WALLET"

    def to_dict(self) -> dict[str, Any]:
        return {
            "publicKey": self.public_key,
            "transactionId": self.transaction_id,
            "paymentType": self.payment_type,
        }


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


@dataclass
class PaymentResponse:
    """
    Parsed payment API response.

    ``raw`` always contains the full JSON response dict for fields
    not covered by the typed attributes.
    """

    status: str
    message: str
    raw: dict[str, Any]

    @property
    def is_successful(self) -> bool:
        """True when Xpresspay marks the transaction as fully settled."""
        payment = self.raw.get("data", {}).get("payment", {})
        return payment.get("paymentResponseCode") == "000"

    @property
    def requires_validation(self) -> bool:
        """True when an OTP/PIN step is still needed."""
        payment = self.raw.get("data", {}).get("payment", {})
        return payment.get("authenticatePaymentResponseCode") == "02"

    @property
    def suggested_authentication(self) -> str | None:
        """Returns 'PIN', 'AVS_VBVSECURECODE', or None."""
        payment = self.raw.get("data", {}).get("payment", {})
        return payment.get("suggestedAuthentication")

    @property
    def auth_url(self) -> str | None:
        """3DSecure iframe URL, present for international AVS cards."""
        payment = self.raw.get("data", {}).get("payment", {})
        return payment.get("authUrl")

    @property
    def unique_key(self) -> str | None:
        payment = self.raw.get("data", {}).get("payment", {})
        return payment.get("uniqueKey")

    @property
    def transaction_reference(self) -> str | None:
        payment = self.raw.get("data", {}).get("payment", {})
        return payment.get("transactionReference")

    @property
    def amount(self) -> str | None:
        payment = self.raw.get("data", {}).get("payment", {})
        return payment.get("amount")

    @property
    def charged_amount(self) -> str | None:
        payment = self.raw.get("data", {}).get("payment", {})
        return payment.get("chargedAmount")

    @property
    def payment_type(self) -> str | None:
        payment = self.raw.get("data", {}).get("payment", {})
        return payment.get("paymentType")

    @property
    def validation_instruction(self) -> str | None:
        """Human-readable instruction for the next customer action."""
        payment = self.raw.get("data", {}).get("payment", {})
        return payment.get("validationInstruction")
