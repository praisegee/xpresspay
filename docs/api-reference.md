# API reference

## XpressPay client

```python
from xpresspay import XpressPay
```

### Constructor

```python
XpressPay(
    public_key: str,
    *,
    sandbox: bool = True,
    timeout: float = 30.0,
)
```

Raises `ValueError` if `public_key` does not start with `XPPUBK-`.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `public_key` | `str` | The configured public key |
| `is_sandbox` | `bool` | `True` when pointing at sandbox |

### Resources

| Attribute | Type | Description |
|-----------|------|-------------|
| `payments` | `PaymentResource` | Initialize and verify transactions |

### Methods

| Method | Description |
|--------|-------------|
| `close()` | Release underlying HTTP connections |
| `__enter__` / `__exit__` | Context manager support |

---

## PaymentResource

Access via `client.payments`.

| Method | Arguments | Returns |
|--------|-----------|---------|
| `initialize(request)` | `InitializeRequest` | `InitializeResponse` |
| `verify(request)` | `VerifyRequest` | `VerifyResponse` |

---

## Request models

```python
from xpresspay import InitializeRequest, VerifyRequest
```

### InitializeRequest

See full field table in [Payments — InitializeRequest fields](card-payments.md#initializerequest-fields).

Method: `to_dict() -> dict`

### VerifyRequest

| Field | Type | Description |
|-------|------|-------------|
| `transaction_id` | `str` | The transaction ID used during initialization |

Method: `to_dict() -> dict`

---

## Response models

### InitializeResponse

| Attribute / Property | Type | Description |
|----------------------|------|-------------|
| `is_successful` | `bool` | `responseCode == "00"` |
| `payment_url` | `str \| None` | Hosted payment page URL |
| `reference` | `str \| None` | Xpresspay transaction reference |
| `response_code` | `str` | Raw API response code |
| `response_message` | `str` | Human-readable API message |
| `raw` | `dict` | Complete JSON response |

### VerifyResponse

| Attribute / Property | Type | Description |
|----------------------|------|-------------|
| `is_successful` | `bool` | `True` when the transaction was settled |
| `amount` | `str \| None` | Transaction amount |
| `currency` | `str \| None` | Currency code |
| `status` | `str \| None` | Status description |
| `payment_type` | `str \| None` | Payment method used |
| `gateway_response` | `str \| None` | Raw gateway message |
| `transaction_id` | `str \| None` | Your original transaction ID |
| `response_code` | `str` | Raw API response code |
| `response_message` | `str` | Human-readable API message |
| `raw` | `dict` | Complete JSON response |

---

## Exceptions

```python
from xpresspay import (
    XpressPayError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ProcessingError,
    NetworkError,
)
```

See the full [Exceptions](exceptions.md) page for details on each class.

---

## Package metadata

```python
import xpresspay

print(xpresspay.__version__)  # "0.2.2"
```
