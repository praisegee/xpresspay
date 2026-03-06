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

## Quick start

```python
from xpresspay import XpressPay

# Reads XPRESSPAY_PUBLIC_KEY from the environment automatically
client = XpressPay(sandbox=True)  # False for production

# Or pass the key explicitly
client = XpressPay(public_key="XPPUBK-...", sandbox=True)
```

## Initialize a payment

```python
from xpresspay import InitializeRequest

response = client.payments.initialize(
    InitializeRequest(
        amount="1000.00",
        email="customer@example.com",
        transaction_id="ORDER-001",
        callback_url="https://yourdomain.com/payment/callback",
    )
)

if response.is_successful:
    # Redirect the customer to the hosted payment page
    print(response.payment_url)
    print(response.reference)
```

## Verify a payment (server-side)

Always verify server-side before fulfilling an order.

```python
from xpresspay import VerifyRequest

result = client.payments.verify(
    VerifyRequest(transaction_id="ORDER-001")
)

if result.is_successful and result.amount == "1000.00":
    print("Payment confirmed:", result.gateway_response)
else:
    print("Not confirmed:", result.status)
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
    response = client.payments.initialize(...)
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
| `NetworkError` | Timeout / connection error |

## Requirements

- Python **3.9+**
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Security

- Your **public key** (`XPPUBK-…`) is sent as a Bearer token in every request.
- Store credentials in environment variables, never in source code.

## Environment variables

| Variable | Description |
|---|---|
| `XPRESSPAY_PUBLIC_KEY` | Public key (`XPPUBK-…`) — picked up automatically if `public_key` is not passed to the client |

## License

Released under the [MIT License](https://github.com/praisegee/xpresspay/blob/main/LICENSE).
