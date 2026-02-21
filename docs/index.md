# xpresspay

**Python SDK for the [Xpress payment gateway](https://www.xpresspayonline.com)**

---

xpresspay lets you accept payments in Nigerian applications with a clean, typed Python API. It handles card payments (local PIN, international AVS/3DSecure), direct bank-account debits, OTP validation, payment verification, and bank listing — with no manual HTTP or encryption code on your side.

## Features

- **Card payments** — full lifecycle: initiate → PIN or AVS auth → OTP → verify
- **Account payments** — bank account direct debit with OTP confirmation
- **3DES-24 encryption** — your secret key never leaves your server
- **Typed models** — dataclasses for every request and response field
- **Typed exceptions** — granular error classes mapped to HTTP status codes
- **httpx-powered** — modern async-ready HTTP client with configurable timeouts
- **Sandbox support** — toggle between sandbox and live with a single flag

## Install

```bash
uv add xpresspay
# or
pip install xpresspay
```

## At a glance

```python
import os
from xpresspay import XpressPay, CardPaymentRequest, PaymentQueryRequest

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

print(response.suggested_authentication)  # "PIN" or "AVS_VBVSECURECODE"
```

## Requirements

- Python **3.9+**
- [`httpx`](https://www.python-httpx.org/) ≥ 0.27
- [`pycryptodome`](https://pycryptodome.readthedocs.io/) ≥ 3.20

Both are installed automatically with the package.

## Security model

| Key | Used for | Leaves your server? |
|-----|----------|---------------------|
| `XPPUBK-…` | Identifying your account in API requests | Yes (safe) |
| `XPSECK-…` | Deriving the local 3DES encryption key | **Never** |

Your secret key is used **only** to encrypt the payload locally before it is sent. Only the ciphertext travels over HTTPS to Xpresspay's servers.

!!! warning "Never commit your keys"
    Store credentials in environment variables or a secrets manager. Never hardcode them in source code.
