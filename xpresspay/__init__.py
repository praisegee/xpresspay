"""
xpresspay — Python SDK for the Xpress payment gateway.

Quick start::

    import os
    from xpresspay import XpressPay
    from xpresspay.models import CardPaymentRequest, CardPinAuthRequest

    client = XpressPay(
        public_key=os.environ["XPRESSPAY_PUBLIC_KEY"],
        secret_key=os.environ["XPRESSPAY_SECRET_KEY"],
        sandbox=True,
    )

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
"""

from .client import XpressPay
from .exceptions import (
    AuthenticationError,
    EncryptionError,
    NetworkError,
    NotFoundError,
    ProcessingError,
    ValidationError,
    XpressPayError,
)
from .models import (
    AccountPaymentRequest,
    CardAvsAuthRequest,
    CardPaymentRequest,
    CardPinAuthRequest,
    OtpValidationRequest,
    PaymentQueryRequest,
    PaymentResponse,
)

__version__ = "0.1.0"
__all__ = [
    # Client
    "XpressPay",
    # Models
    "CardPaymentRequest",
    "CardPinAuthRequest",
    "CardAvsAuthRequest",
    "AccountPaymentRequest",
    "OtpValidationRequest",
    "PaymentQueryRequest",
    "PaymentResponse",
    # Exceptions
    "XpressPayError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "ProcessingError",
    "EncryptionError",
    "NetworkError",
]
