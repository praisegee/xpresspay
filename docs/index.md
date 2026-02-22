# xpresspay

**Python SDK for the [Xpress payment gateway](https://www.xpresspayments.com)**

---

xpresspay lets you accept payments in Nigerian applications with a clean, typed Python API. It handles payment initialization and server-side verification — with no manual HTTP or encryption code on your side.

## Features

- **Hosted payment page** — initialize a transaction and redirect the customer to Xpresspay's secure payment page
- **Server-side verification** — confirm payment status before fulfilling orders
- **Typed models** — dataclasses for every request and response field
- **Typed exceptions** — granular error classes mapped to HTTP status codes
- **httpx-powered** — modern HTTP client with configurable timeouts
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
from xpresspay import XpressPay, InitializeRequest, VerifyRequest

client = XpressPay(
    public_key=os.environ["XPRESSPAY_PUBLIC_KEY"],
    sandbox=True,
)

# Initialize — get a payment URL to redirect your customer to
response = client.payments.initialize(
    InitializeRequest(
        amount="1000.00",
        email="customer@example.com",
        transaction_id="ORDER-001",
        callback_url="https://yourdomain.com/payment/callback",
    )
)

if response.is_successful:
    print(response.payment_url)   # redirect customer here

# Verify — confirm payment server-side before fulfilling the order
result = client.payments.verify(
    VerifyRequest(transaction_id="ORDER-001")
)

print(result.is_successful)   # True / False
print(result.amount)          # "1000.00"
```

## Requirements

- Python **3.9+**
- [`httpx`](https://www.python-httpx.org/) ≥ 0.27

Installed automatically with the package.

## Security model

| Key | Used for | Transmitted? |
|-----|----------|--------------|
| `XPPUBK-…` | Bearer token in every API request | Yes (safe) |

!!! warning "Never commit your keys"
    Store credentials in environment variables or a secrets manager. Never hardcode them in source code.

## License

Released under the [MIT License](https://github.com/praisegee/xpresspay/blob/main/LICENSE).
