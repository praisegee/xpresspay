# Exceptions

All SDK exceptions inherit from `XpressPayError` so you can catch them all with a single clause, or handle each type individually for fine-grained control.

## Hierarchy

```
XpressPayError
├── AuthenticationError   (HTTP 401)
├── ValidationError       (HTTP 400)
├── NotFoundError         (HTTP 404)
├── ProcessingError       (HTTP 5xx)
├── EncryptionError       (local 3DES failure)
└── NetworkError          (timeout / connection refused)
```

---

## Reference

### `XpressPayError`

Base class for all SDK errors.

```python
from xpresspay import XpressPayError
```

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Human-readable error description |
| `status_code` | `int \| None` | HTTP status code, or `None` for local errors |

---

### `AuthenticationError`

Raised when the API returns HTTP **401**. Usually means your public key is wrong, missing, or the key does not match the environment (sandbox vs live).

```python
from xpresspay import AuthenticationError

try:
    client.cards.initiate(...)
except AuthenticationError as e:
    print(e.message)        # "Invalid public key"
    print(e.status_code)    # 401
```

---

### `ValidationError`

Raised when the API returns HTTP **400**. The request was well-formed but contained invalid data (e.g. missing required fields, wrong card number format).

```python
from xpresspay import ValidationError

try:
    client.cards.initiate(...)
except ValidationError as e:
    print(e.message)     # "transactionId is required"
    print(e.error_type)  # error sub-type returned by the API, if any
    print(e.status_code) # 400
```

| Extra attribute | Type | Description |
|-----------------|------|-------------|
| `error_type` | `str \| None` | Error sub-type from the API response body |

---

### `NotFoundError`

Raised when the API returns HTTP **404**. Typically means the `transaction_id` passed to `query()` or `validate_otp()` does not exist.

```python
from xpresspay import NotFoundError

try:
    client.cards.query(...)
except NotFoundError as e:
    print(e.message)     # "Transaction not found"
    print(e.status_code) # 404
```

---

### `ProcessingError`

Raised when the API returns HTTP **5xx**. The Xpresspay server encountered an internal error. These are generally safe to retry after a short wait.

```python
from xpresspay import ProcessingError

try:
    client.cards.initiate(...)
except ProcessingError as e:
    print(e.message)     # "Internal server error"
    print(e.status_code) # 500, 502, 503, …
```

---

### `EncryptionError`

Raised locally when the 3DES encryption step fails — before any network request is made. Common causes:

- Secret key is empty or too short
- Secret key does not start with `XPSECK-`
- Payload contains non-serialisable Python objects

```python
from xpresspay import EncryptionError

try:
    client.cards.initiate(...)
except EncryptionError as e:
    print(e.message)     # "Secret key is too short …"
    print(e.status_code) # None (local error)
```

---

### `NetworkError`

Raised when `httpx` fails to complete the request due to a network-level problem: timeout, DNS failure, connection refused, etc.

These errors are **safe to retry** — no charge was made because the request never reached Xpresspay's servers.

```python
from xpresspay import NetworkError

try:
    client.cards.initiate(...)
except NetworkError as e:
    print(e.message)  # "Request timed out: …" or "Network error: …"
    # Safe to retry
```

---

## Recommended handling pattern

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

try:
    response = client.cards.initiate(...)

except AuthenticationError:
    # Wrong key or wrong environment — fix config, do not retry
    raise

except ValidationError as e:
    # Bad input — show e.message to the developer / log it
    print("Invalid request:", e.message, e.error_type)

except NotFoundError:
    # Transaction ID unknown — do not retry with same ID
    raise

except ProcessingError:
    # Server-side error — wait, then retry
    import time; time.sleep(2)
    # ... retry logic

except NetworkError:
    # No request reached Xpresspay — safe to retry immediately
    # ... retry logic

except EncryptionError as e:
    # Local configuration error — fix secret key
    raise RuntimeError("Encryption misconfigured") from e

except XpressPayError as e:
    # Catch-all for any other SDK error
    print(f"Unexpected error ({e.status_code}): {e.message}")
```
