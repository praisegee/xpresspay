# API reference

## XpressPay client

```python
from xpresspay import XpressPay
```

### Constructor

```python
XpressPay(
    public_key: str,
    secret_key: str,
    *,
    sandbox: bool = True,
    timeout: float = 30.0,
)
```

Raises `ValueError` if either key has the wrong prefix.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `public_key` | `str` | The configured public key |
| `is_sandbox` | `bool` | `True` when pointing at sandbox |

### Resources

| Attribute | Type | Description |
|-----------|------|-------------|
| `cards` | `CardResource` | Card payment operations |
| `accounts` | `AccountResource` | Bank account payment operations |
| `banks` | `BanksResource` | Bank listing |

### Methods

| Method | Description |
|--------|-------------|
| `close()` | Release underlying HTTP connections |
| `__enter__` / `__exit__` | Context manager support |

---

## CardResource

Access via `client.cards`.

| Method | Arguments | Returns |
|--------|-----------|---------|
| `initiate(request)` | `CardPaymentRequest` | `PaymentResponse` |
| `authenticate_pin(request)` | `CardPinAuthRequest` | `PaymentResponse` |
| `authenticate_avs(request)` | `CardAvsAuthRequest` | `PaymentResponse` |
| `validate_otp(request)` | `OtpValidationRequest` | `PaymentResponse` |
| `query(request)` | `PaymentQueryRequest` | `PaymentResponse` |

---

## AccountResource

Access via `client.accounts`.

| Method | Arguments | Returns |
|--------|-----------|---------|
| `initiate(request)` | `AccountPaymentRequest` | `PaymentResponse` |
| `validate_otp(request)` | `OtpValidationRequest` | `PaymentResponse` |
| `query(request)` | `PaymentQueryRequest` | `PaymentResponse` |

---

## BanksResource

Access via `client.banks`.

| Method | Arguments | Returns |
|--------|-----------|---------|
| `list()` | — | `list[Bank]` |

### Bank

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Bank display name |
| `code` | `str` | Bank code for payment requests |
| `raw` | `dict` | Full API response entry |

---

## Request models

All models are plain Python dataclasses. Import them from `xpresspay`:

```python
from xpresspay import (
    CardPaymentRequest,
    CardPinAuthRequest,
    CardAvsAuthRequest,
    AccountPaymentRequest,
    OtpValidationRequest,
    PaymentQueryRequest,
)
```

### CardPaymentRequest

See full field table in [Card payments — Step 1](card-payments.md#cardpaymentrequest-fields).

Method: `to_encrypt_dict() -> dict` — returns the dict that gets encrypted and sent as the `request` field.

### CardPinAuthRequest

| Field | Type | Description |
|-------|------|-------------|
| `public_key` | `str` | `XPPUBK-…` |
| `transaction_id` | `str` | Your order ID |
| `pin` | `str` | 4-digit card PIN |

### CardAvsAuthRequest

| Field | Type | Description |
|-------|------|-------------|
| `public_key` | `str` | `XPPUBK-…` |
| `transaction_id` | `str` | Your order ID |
| `billing_zip` | `str \| None` | |
| `billing_city` | `str \| None` | |
| `billing_address` | `str \| None` | |
| `billing_state` | `str \| None` | |
| `billing_country` | `str \| None` | |

### AccountPaymentRequest

See full field table in [Account payments — Step 1](account-payments.md#accountpaymentrequest-fields).

Method: `to_encrypt_dict() -> dict`

### OtpValidationRequest

| Field | Type | Description |
|-------|------|-------------|
| `public_key` | `str` | `XPPUBK-…` |
| `transaction_id` | `str` | Your order ID |
| `otp` | `str` | OTP from customer |
| `payment_type` | `str` | `"CARD"` or `"ACCOUNT"` |

### PaymentQueryRequest

| Field | Type | Description |
|-------|------|-------------|
| `public_key` | `str` | `XPPUBK-…` |
| `transaction_id` | `str` | Your order ID |
| `payment_type` | `str` | `"CARD"`, `"ACCOUNT"`, `"QR"`, `"USSD"`, `"WALLET"` |

---

## PaymentResponse

Returned by every resource method.

```python
from xpresspay import PaymentResponse
```

| Attribute / Property | Type | Description |
|----------------------|------|-------------|
| `status` | `str` | Top-level status string from API |
| `message` | `str` | Top-level message string from API |
| `raw` | `dict` | Complete JSON response |
| `is_successful` | `bool` | `paymentResponseCode == "000"` |
| `requires_validation` | `bool` | `authenticatePaymentResponseCode == "02"` |
| `suggested_authentication` | `str \| None` | `"PIN"`, `"AVS_VBVSECURECODE"`, or `None` |
| `auth_url` | `str \| None` | 3DSecure iframe URL |
| `transaction_reference` | `str \| None` | Xpresspay's transaction reference |
| `unique_key` | `str \| None` | Xpresspay's unique payment key |
| `amount` | `str \| None` | Original amount |
| `charged_amount` | `str \| None` | Amount actually charged |
| `payment_type` | `str \| None` | `"CARD"` or `"ACCOUNT"` |
| `validation_instruction` | `str \| None` | Human-readable next-step hint |

---

## Exceptions

```python
from xpresspay import (
    XpressPayError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ProcessingError,
    EncryptionError,
    NetworkError,
)
```

See the full [Exceptions](exceptions.md) page for details on each class.

---

## Package metadata

```python
import xpresspay

print(xpresspay.__version__)  # "0.1.0"
```
