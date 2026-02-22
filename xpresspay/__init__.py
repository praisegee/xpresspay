"""
xpresspay — Python SDK for the Xpress payment gateway.

Quick start::

    import os
    from xpresspay import XpressPay, InitializeRequest

    client = XpressPay(
        public_key=os.environ["XPRESSPAY_PUBLIC_KEY"],
        sandbox=True,
    )

    response = client.payments.initialize(
        InitializeRequest(
            amount="1000.00",
            email="customer@example.com",
            transaction_id="ORDER-001",
        )
    )

    if response.is_successful:
        print(response.payment_url)   # redirect customer here
"""

from .client import XpressPay
from .exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    ProcessingError,
    ValidationError,
    XpressPayError,
)
from .models import (
    InitializeRequest,
    InitializeResponse,
    VerifyRequest,
    VerifyResponse,
)

__version__ = "0.2.1"
__all__ = [
    # Client
    "XpressPay",
    # Models
    "InitializeRequest",
    "InitializeResponse",
    "VerifyRequest",
    "VerifyResponse",
    # Exceptions
    "XpressPayError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "ProcessingError",
    "NetworkError",
]
