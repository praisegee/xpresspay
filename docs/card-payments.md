# Payments

The Xpresspay integration uses a hosted payment page flow — you initialize a transaction from your server, then redirect the customer to Xpresspay's hosted page to complete payment. Once the customer pays, they are sent back to your `callback_url`.

```
Initialize (server-side)
       │
       └─ Redirect customer to payment_url
               │
               └─ Customer pays on Xpresspay hosted page
                       │
                       └─ Redirect to callback_url
                               │
                               └─ Verify (server-side) ← always do this
```

---

## Initialize a transaction

```python
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
        callback_url="https://yourdomain.com/payment/callback",
    )
)

if response.is_successful:
    # Redirect the customer to the hosted payment page
    print(response.payment_url)
    print(response.reference)
```

### InitializeRequest fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | `str` | ✓ | Amount to charge, e.g. `"1000.00"` |
| `email` | `str` | ✓ | Customer's email address |
| `transaction_id` | `str` | ✓ | Your unique transaction ID (6–30 characters) |
| `currency` | `str` | | Default: `"NGN"` |
| `product_id` | `str` | | Unique product identifier |
| `product_description` | `str` | | Description shown on the payment page |
| `callback_url` | `str` | | URL the customer is redirected to after payment |
| `body_color` | `str` | | Custom hex colour for the payment page body |
| `button_color` | `str` | | Custom hex colour for payment page buttons |
| `footer_text` | `str` | | Custom footer text on the payment page |
| `footer_logo` | `str` | | URL to your logo shown in the page footer |
| `split_payment_reference` | `str` | | Reference for a pre-configured split payment |
| `is_split_payment` | `bool` | | Set `True` to enable split settlement |
| `is_api_user` | `bool` | | Default: `True` — set when integrating via API |
| `merchant_name` | `str` | | Your business name shown on the payment page |
| `logo_url` | `str` | | URL to your business logo |
| `mode` | `str` | | Payment mode |
| `apply_conveniency_charge` | `bool` | | Pass the convenience charge to the customer |
| `is_recurring` | `bool` | | Mark transaction as recurring |
| `metadata` | `list[dict]` | | Extra data: `[{"name": "key", "value": "val"}]` |

### InitializeResponse properties

| Property | Type | Description |
|----------|------|-------------|
| `is_successful` | `bool` | `True` when `responseCode == "00"` |
| `payment_url` | `str \| None` | Hosted payment page URL — redirect the customer here |
| `reference` | `str \| None` | Transaction reference from Xpresspay |
| `response_code` | `str` | Raw API response code |
| `response_message` | `str` | Human-readable API message |
| `raw` | `dict` | Full JSON response |

---

## Verify a payment

!!! danger "Always verify before fulfilling an order"
    Never trust the client-side redirect. Always confirm the payment
    server-side before delivering goods or services.

```python
from xpresspay import VerifyRequest

result = client.payments.verify(
    VerifyRequest(transaction_id="ORDER-001")
)

if result.is_successful and result.amount == "1000.00":
    # Safe to fulfill the order
    print("Confirmed:", result.gateway_response)
else:
    print("Not confirmed:", result.status)
```

### VerifyResponse properties

| Property | Type | Description |
|----------|------|-------------|
| `is_successful` | `bool` | `True` when the transaction was successfully settled |
| `amount` | `str \| None` | Transaction amount |
| `currency` | `str \| None` | Currency code, e.g. `"NGN"` |
| `status` | `str \| None` | Status description, e.g. `"Transaction Successful"` |
| `payment_type` | `str \| None` | e.g. `"Card"` |
| `gateway_response` | `str \| None` | Raw gateway message |
| `transaction_id` | `str \| None` | Your original transaction ID |
| `response_code` | `str` | Raw API response code |
| `response_message` | `str` | Human-readable API message |
| `raw` | `dict` | Full JSON response |

---

## Complete example

```python
import os
from xpresspay import (
    XpressPay,
    InitializeRequest,
    VerifyRequest,
    AuthenticationError,
    ValidationError,
    NetworkError,
)

client = XpressPay(
    public_key=os.environ["XPRESSPAY_PUBLIC_KEY"],
    sandbox=True,
)

try:
    # 1 — Initialize
    resp = client.payments.initialize(
        InitializeRequest(
            amount="1000.00",
            email="customer@example.com",
            transaction_id="ORDER-001",
            callback_url="https://yourdomain.com/payment/callback",
            merchant_name="My Store",
        )
    )

    if resp.is_successful:
        print("Redirect customer to:", resp.payment_url)

    # 2 — After customer returns to callback_url, verify server-side
    result = client.payments.verify(
        VerifyRequest(transaction_id="ORDER-001")
    )

    if result.is_successful:
        print("Payment confirmed:", result.gateway_response)

except ValidationError as e:
    print("Bad request:", e.message)
except AuthenticationError:
    print("Check your API key")
except NetworkError:
    print("Network issue — safe to retry")
finally:
    client.close()
```
