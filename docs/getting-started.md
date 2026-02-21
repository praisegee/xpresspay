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

1. **Create an account** — go to [xpresspayments.com](https://www.xpresspayments.com) and sign up for a merchant account. You will receive a confirmation email to verify your address.

2. **Log in to the dashboard** — after email verification, sign in at the merchant portal.

3. **Locate your API keys** — navigate to **Settings → API Keys** (or **Developer → API Keys**, depending on the dashboard version). You will see:
    - **Public key** — prefixed `XPPUBK-…`. Safe to use on the server side in API requests.
    - **Secret key** — prefixed `XPSECK-…`. Used locally to encrypt payloads. **Never expose this in client-side code, logs, or version control.**

4. **Sandbox vs live** — the dashboard provides a separate set of keys for each environment. Use your **sandbox keys** while `sandbox=True` and your **live keys** when you switch to `sandbox=False`.

!!! note "Account approval"
    Xpresspay may require business verification before your live keys are activated. Sandbox keys are typically available immediately after signup, so you can start integrating right away.

## Environment variables

Never hardcode your keys. Export them from your shell or load them via a `.env` file:

```bash
export XPRESSPAY_PUBLIC_KEY="XPPUBK-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-X"
export XPRESSPAY_SECRET_KEY="XPSECK-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-X"
```

## Create a client

```python
import os
from xpresspay import XpressPay

client = XpressPay(
    public_key=os.environ["XPRESSPAY_PUBLIC_KEY"],
    secret_key=os.environ["XPRESSPAY_SECRET_KEY"],
    sandbox=True,   # set False for live/production
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `public_key` | `str` | required | Must start with `XPPUBK-` |
| `secret_key` | `str` | required | Must start with `XPSECK-`. Never transmitted. |
| `sandbox` | `bool` | `True` | `True` → sandbox, `False` → live |
| `timeout` | `float` | `30.0` | Request timeout in seconds |

!!! tip "Use as a context manager"
    The client implements `__enter__` / `__exit__` so you can use it in a `with` block and HTTP connections are released automatically:

    ```python
    with XpressPay(...) as client:
        response = client.cards.initiate(...)
    ```

## Sandbox vs live

| Mode | Base URL |
|------|----------|
| `sandbox=True` | `https://xpresspayonlineapisandbox.xpresspayments.com` |
| `sandbox=False` | `https://api.xpresspayonline.com` |

Use sandbox keys (issued separately from your live keys) when `sandbox=True`.

## Check the environment

```python
print(client.public_key)   # XPPUBK-…
print(client.is_sandbox)   # True / False
```

## Next steps

- [Card payments](card-payments.md) — charge a debit or credit card
- [Account payments](account-payments.md) — debit a bank account directly
- [Exceptions](exceptions.md) — handle errors gracefully
