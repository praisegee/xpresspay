# xpresspay

A Python SDK for integrating the [Xpress payment gateway](https://www.xpresspayonline.com) into your application.

Supports card payments (PIN, AVS/3DSecure), direct bank-account debits, payment verification, and banks listing. Built on [`httpx`](https://www.python-httpx.org/) with 3DES-24 encryption as required by the Xpresspay API.

## Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

```bash
uv add xpresspay
# or
pip install xpresspay
```

## Security

- Your **secret key** (`XPSECK-…`) is used **only for local encryption** — it is never sent over the network.
- Only the resulting ciphertext travels to Xpresspay's servers over HTTPS.
- Store credentials in environment variables, never in source code.

## Quick start

```python
import os
from xpresspay import XpressPay

client = XpressPay(
    public_key=os.environ["XPRESSPAY_PUBLIC_KEY"],
    secret_key=os.environ["XPRESSPAY_SECRET_KEY"],
    sandbox=True,   # False for production
)
```

## Card payment flow

### 1 — Initiate

```python
from xpresspay import CardPaymentRequest

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
        phone_number="08012345678",
        first_name="Ada",
        last_name="Okonkwo",
    )
)
```

### 2a — Authenticate (Nigerian cards — PIN)

```python
from xpresspay import CardPinAuthRequest

if response.suggested_authentication == "PIN":
    auth = client.cards.authenticate_pin(
        CardPinAuthRequest(
            public_key=client.public_key,
            transaction_id="ORDER-001",
            pin="1234",
        )
    )
```

### 2b — Authenticate (international cards — AVS/3DSecure)

```python
from xpresspay import CardAvsAuthRequest

if response.suggested_authentication == "AVS_VBVSECURECODE":
    auth = client.cards.authenticate_avs(
        CardAvsAuthRequest(
            public_key=client.public_key,
            transaction_id="ORDER-001",
            billing_zip="07205",
            billing_city="Hillside",
            billing_address="470 Mundet PI",
            billing_state="NJ",
            billing_country="US",
        )
    )
    # If auth.auth_url is set, render it in an iframe for 3DSecure
```

### 3 — Validate OTP

```python
from xpresspay import OtpValidationRequest

validated = client.cards.validate_otp(
    OtpValidationRequest(
        public_key=client.public_key,
        transaction_id="ORDER-001",
        otp="123456",
        payment_type="CARD",
    )
)
```

### 4 — Verify server-side (always do this before fulfilling orders)

```python
from xpresspay import PaymentQueryRequest

result = client.cards.query(
    PaymentQueryRequest(
        public_key=client.public_key,
        transaction_id="ORDER-001",
        payment_type="CARD",
    )
)

if result.is_successful and result.amount == "5000":
    print("Payment confirmed:", result.transaction_reference)
else:
    print("Not confirmed:", result.raw)
```

## Bank account payment flow

```python
from xpresspay import AccountPaymentRequest, OtpValidationRequest, PaymentQueryRequest

banks = client.banks.list()
access_bank = next(b for b in banks if "Access" in b.name)

response = client.accounts.initiate(
    AccountPaymentRequest(
        public_key=client.public_key,
        account_number="0690000031",
        bank_code=access_bank.code,
        amount="10000",
        email="customer@example.com",
        transaction_id="ORDER-002",
        # date_of_birth="01011990",  # required for Zenith / UBA
        # bvn="12345678901",         # required for UBA
        # redirect_url="https://yourdomain.com/callback",  # required for GTB / First Bank
    )
)

validated = client.accounts.validate_otp(
    OtpValidationRequest(
        public_key=client.public_key,
        transaction_id="ORDER-002",
        otp="123456",
        payment_type="ACCOUNT",
    )
)

result = client.accounts.query(
    PaymentQueryRequest(
        public_key=client.public_key,
        transaction_id="ORDER-002",
        payment_type="ACCOUNT",
    )
)
assert result.is_successful
```

## Exception handling

```python
from xpresspay import (
    XpressPayError,
    AuthenticationError,
    ValidationError,
    NetworkError,
)

try:
    response = client.cards.initiate(...)
except AuthenticationError:
    ...  # invalid / missing API key
except ValidationError as e:
    print(e.message, e.error_type)
except NetworkError:
    ...  # timeout — safe to retry
except XpressPayError:
    ...  # catch-all
```

## Exception reference

| Exception | Trigger |
|---|---|
| `XpressPayError` | Base class |
| `AuthenticationError` | HTTP 401 |
| `ValidationError` | HTTP 400 |
| `NotFoundError` | HTTP 404 |
| `ProcessingError` | HTTP 5xx |
| `EncryptionError` | Local 3DES failure |
| `NetworkError` | Timeout / connection error |

## Development

```bash
git clone https://github.com/praisegod/xpresspay
cd xpresspay
uv sync --group dev
uv run pytest
uv run ruff check xpresspay/ tests/
```

## Environment variables

| Variable | Description |
|---|---|
| `XPRESSPAY_PUBLIC_KEY` | Public key (`XPPUBK-…`) |
| `XPRESSPAY_SECRET_KEY` | Secret key (`XPSECK-…`) — **server-side only** |

## License

MIT
