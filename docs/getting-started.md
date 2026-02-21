# Getting started

## Installation

=== "uv (recommended)"

    ```bash
    uv add xpresspay
    ```

=== "pip"

    ```bash
    pip install xpresspay
    ```

## Obtaining your API keys

Xpresspay issues two separate key pairs: one for **sandbox** (testing) and one for **live** (production). Get them from the merchant dashboard:

1. **Create an account** — go to [myxpresspay.com](https://myxpresspay.com) and sign up for a merchant account. You will receive a confirmation email to verify your address.

2. **Log in to the dashboard** — after email verification, sign in at the merchant portal.

3. **Locate your API keys** — go to [myxpresspay.com/settings/keys](https://myxpresspay.com/settings/keys). You will see:
    - **Public key** — prefixed `XPPUBK-…`. This is your Bearer token for all API requests.

4. **Sandbox vs live** — the dashboard provides a separate set of keys for each environment. Use your **sandbox keys** while `sandbox=True` and your **live keys** when you switch to `sandbox=False`.

!!! note "Account approval"
    Xpresspay may require business verification before your live keys are activated. Sandbox keys are typically available immediately after signup, so you can start integrating right away.

## Environment variables

Never hardcode your keys. Export them from your shell or load them via a `.env` file:

```bash
export XPRESSPAY_PUBLIC_KEY="XPPUBK-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-X"
```

## Create a client

```python
import os
from xpresspay import XpressPay

client = XpressPay(
    public_key=os.environ["XPRESSPAY_PUBLIC_KEY"],
    sandbox=True,   # set False for live/production
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `public_key` | `str` | required | Must start with `XPPUBK-` |
| `sandbox` | `bool` | `True` | `True` → sandbox, `False` → live |
| `timeout` | `float` | `30.0` | Request timeout in seconds |

!!! tip "Use as a context manager"
    The client implements `__enter__` / `__exit__` so you can use it in a `with` block and HTTP connections are released automatically:

    ```python
    with XpressPay(...) as client:
        response = client.payments.initialize(...)
    ```

## Sandbox vs live

| Mode | Base URL |
|------|----------|
| `sandbox=True` | `https://pgsandbox.xpresspayments.com:6004` |
| `sandbox=False` | `https://myxpresspay.com:6004` |

Use sandbox keys (issued separately from your live keys) when `sandbox=True`.

## Next steps

- [Payments](card-payments.md) — initialize a transaction and verify payment
- [Exceptions](exceptions.md) — handle errors gracefully
