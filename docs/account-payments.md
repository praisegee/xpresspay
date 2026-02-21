# Account payments

Account payments debit a customer's bank account directly. The customer authorises the debit by entering an OTP sent to their registered phone number.

```
List banks  →  Initiate  →  validate_otp()  →  query()
```

---

## Step 0 — List supported banks

```python
banks = client.banks.list()

for bank in banks:
    print(f"{bank.name}: {bank.code}")
# Access Bank: 044
# First Bank: 011
# GTBank: 058
# ...
```

Each `Bank` object has:

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Human-readable bank name |
| `code` | `str` | Bank code required for payment initiation |
| `raw` | `dict` | Full JSON entry for unlisted fields |

---

## Step 1 — Initiate

```python
from xpresspay import AccountPaymentRequest

response = client.accounts.initiate(
    AccountPaymentRequest(
        public_key=client.public_key,
        account_number="0690000031",
        bank_code="044",        # from banks.list()
        amount="10000",
        email="customer@example.com",
        transaction_id="ORDER-002",
    )
)
```

### AccountPaymentRequest fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `public_key` | `str` | ✓ | Your `XPPUBK-…` key |
| `account_number` | `str` | ✓ | Customer's bank account number |
| `bank_code` | `str` | ✓ | Bank code from `banks.list()` |
| `amount` | `str` | ✓ | Amount in kobo |
| `email` | `str` | ✓ | Customer email |
| `transaction_id` | `str` | ✓ | Your unique order ID |
| `currency` | `str` | | Default: `"NGN"` |
| `country` | `str` | | Default: `"NG"` |
| `phone_number` | `str` | | Customer phone |
| `first_name` | `str` | | Customer first name |
| `last_name` | `str` | | Customer last name |
| `ip` | `str` | | Customer IP address |
| `device_finger_print` | `str` | | Browser fingerprint |
| `date_of_birth` | `str` | See note | `DDMMYYYY` — required for Zenith and UBA |
| `bvn` | `str` | See note | Required for UBA accounts |
| `redirect_url` | `str` | See note | Required for GTBank and First Bank |

### Bank-specific requirements

| Bank | Extra required fields |
|------|-----------------------|
| Zenith Bank | `date_of_birth` (DDMMYYYY) |
| UBA | `date_of_birth` + `bvn` |
| GTBank | `redirect_url` |
| First Bank | `redirect_url` |
| Others | None |

```python
# Zenith / UBA example
response = client.accounts.initiate(
    AccountPaymentRequest(
        public_key=client.public_key,
        account_number="0123456789",
        bank_code="057",            # Zenith
        amount="5000",
        email="customer@example.com",
        transaction_id="ORDER-003",
        date_of_birth="01011990",   # DDMMYYYY
    )
)

# GTBank / First Bank example
response = client.accounts.initiate(
    AccountPaymentRequest(
        public_key=client.public_key,
        account_number="0123456789",
        bank_code="058",            # GTBank
        amount="5000",
        email="customer@example.com",
        transaction_id="ORDER-004",
        redirect_url="https://yourdomain.com/payment/callback",
    )
)
```

---

## Step 2 — Validate OTP

After initiation the customer receives an OTP on the phone number registered to their bank account.

```python
from xpresspay import OtpValidationRequest

validated = client.accounts.validate_otp(
    OtpValidationRequest(
        public_key=client.public_key,
        transaction_id="ORDER-002",
        otp="123456",
        payment_type="ACCOUNT",     # note: "ACCOUNT", not "CARD"
    )
)
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `public_key` | `str` | ✓ | Your `XPPUBK-…` key |
| `transaction_id` | `str` | ✓ | Same ID used in initiate |
| `otp` | `str` | ✓ | OTP entered by the customer |
| `payment_type` | `str` | ✓ | Must be `"ACCOUNT"` |

---

## Step 3 — Verify server-side

```python
from xpresspay import PaymentQueryRequest

result = client.accounts.query(
    PaymentQueryRequest(
        public_key=client.public_key,
        transaction_id="ORDER-002",
        payment_type="ACCOUNT",
    )
)

if result.is_successful and result.amount == "10000":
    print("Debit confirmed:", result.transaction_reference)
else:
    print("Not settled:", result.raw)
```

See [Card payments — PaymentResponse properties](card-payments.md#paymentresponse-properties) for a full description of all response attributes.

---

## Complete example

```python
import os
from xpresspay import (
    XpressPay,
    AccountPaymentRequest,
    OtpValidationRequest,
    PaymentQueryRequest,
    ValidationError,
    NetworkError,
)

client = XpressPay(
    public_key=os.environ["XPRESSPAY_PUBLIC_KEY"],
    secret_key=os.environ["XPRESSPAY_SECRET_KEY"],
    sandbox=True,
)

try:
    # 0 — Pick a bank
    banks = client.banks.list()
    access = next(b for b in banks if "Access" in b.name)

    # 1 — Initiate debit
    resp = client.accounts.initiate(
        AccountPaymentRequest(
            public_key=client.public_key,
            account_number="0690000031",
            bank_code=access.code,
            amount="10000",
            email="customer@example.com",
            transaction_id="ORDER-002",
        )
    )

    # 2 — Validate OTP
    otp = input("Enter the OTP sent to your phone: ")
    client.accounts.validate_otp(
        OtpValidationRequest(
            public_key=client.public_key,
            transaction_id="ORDER-002",
            otp=otp,
            payment_type="ACCOUNT",
        )
    )

    # 3 — Verify
    result = client.accounts.query(
        PaymentQueryRequest(
            public_key=client.public_key,
            transaction_id="ORDER-002",
            payment_type="ACCOUNT",
        )
    )

    if result.is_successful:
        print("Debit confirmed:", result.transaction_reference)

except ValidationError as e:
    print("Validation error:", e.message)
except NetworkError:
    print("Network issue — safe to retry")
finally:
    client.close()
```
