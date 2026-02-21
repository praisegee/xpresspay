# Card payments

A card payment goes through up to four steps depending on the card type.

```
Initiate
   │
   ├─ suggested_authentication == "PIN"
   │       └─ authenticate_pin()  →  validate_otp()  →  query()
   │
   └─ suggested_authentication == "AVS_VBVSECURECODE"
           └─ authenticate_avs()
                   ├─ auth_url present  →  (iframe 3DSecure)  →  query()
                   └─ requires_validation  →  validate_otp()  →  query()
```

---

## Step 1 — Initiate

Encrypt and submit the card details. The response tells you what the next step is.

```python
from xpresspay import XpressPay, CardPaymentRequest

response = client.cards.initiate(
    CardPaymentRequest(
        public_key=client.public_key,
        card_number="5438898014560229",
        cvv="789",
        expiry_month="09",
        expiry_year="25",
        amount="5000",          # in kobo (NGN) or smallest currency unit
        email="customer@example.com",
        transaction_id="ORDER-001",

        # Optional but recommended
        phone_number="08012345678",
        first_name="Ada",
        last_name="Okonkwo",
        currency="NGN",         # default
        country="NG",           # default
    )
)
```

### CardPaymentRequest fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `public_key` | `str` | ✓ | Your `XPPUBK-…` key |
| `card_number` | `str` | ✓ | 16-digit card number |
| `cvv` | `str` | ✓ | 3 or 4 digit security code |
| `expiry_month` | `str` | ✓ | Two-digit month, e.g. `"09"` |
| `expiry_year` | `str` | ✓ | Two-digit year, e.g. `"25"` |
| `amount` | `str` | ✓ | Amount in kobo (100 kobo = ₦1) |
| `email` | `str` | ✓ | Customer email |
| `transaction_id` | `str` | ✓ | Your unique order/transaction ID |
| `currency` | `str` | | Default: `"NGN"` |
| `country` | `str` | | Default: `"NG"` |
| `phone_number` | `str` | | Customer phone |
| `first_name` | `str` | | Customer first name |
| `last_name` | `str` | | Customer last name |
| `ip` | `str` | | Customer IP address |
| `device_finger_print` | `str` | | Browser fingerprint |
| `redirect_url` | `str` | | Callback URL after 3DSecure |
| `billing_zip` | `str` | | Required for AVS cards |
| `billing_city` | `str` | | Required for AVS cards |
| `billing_address` | `str` | | Required for AVS cards |
| `billing_state` | `str` | | Required for AVS cards |
| `billing_country` | `str` | | Required for AVS cards |
| `meta` | `list[dict]` | | Key-value metadata pairs |

### Reading the response

```python
print(response.suggested_authentication)
# "PIN"               → local Nigerian card, needs PIN
# "AVS_VBVSECURECODE" → international card, needs billing address
# None                → already settled (rare on first call)

print(response.is_successful)     # True if paymentResponseCode == "000"
print(response.requires_validation)  # True if OTP step is pending
```

---

## Step 2a — PIN authentication (Nigerian cards)

```python
from xpresspay import CardPinAuthRequest

if response.suggested_authentication == "PIN":
    auth = client.cards.authenticate_pin(
        CardPinAuthRequest(
            public_key=client.public_key,
            transaction_id="ORDER-001",
            pin="1234",
        )
    )
    # Customer typically receives an OTP on their phone next
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `public_key` | `str` | ✓ | Your `XPPUBK-…` key |
| `transaction_id` | `str` | ✓ | Same ID used in initiate |
| `pin` | `str` | ✓ | 4-digit card PIN |

After a successful PIN submission, proceed to [Step 3 — Validate OTP](#step-3-validate-otp).

---

## Step 2b — AVS authentication (international cards)

```python
from xpresspay import CardAvsAuthRequest

if response.suggested_authentication == "AVS_VBVSECURECODE":
    auth = client.cards.authenticate_avs(
        CardAvsAuthRequest(
            public_key=client.public_key,
            transaction_id="ORDER-001",
            billing_zip="07205",
            billing_city="Hillside",
            billing_address="470 Mundet Pl",
            billing_state="NJ",
            billing_country="US",
        )
    )

    if auth.auth_url:
        # Render auth.auth_url in an iframe for 3DSecure flow
        print("Redirect to:", auth.auth_url)
    elif auth.requires_validation:
        # OTP sent — proceed to validate_otp()
        pass
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `public_key` | `str` | ✓ | Your `XPPUBK-…` key |
| `transaction_id` | `str` | ✓ | Same ID used in initiate |
| `billing_zip` | `str` | | Postal/ZIP code |
| `billing_city` | `str` | | City |
| `billing_address` | `str` | | Street address |
| `billing_state` | `str` | | State/province code |
| `billing_country` | `str` | | Two-letter ISO country code |

### 3DSecure iframe flow

When `auth.auth_url` is present, embed it in a page:

```html
<iframe src="{{ auth_url }}" width="600" height="400"></iframe>
```

After the customer completes 3DSecure in the iframe, call `query()` server-side to confirm the payment.

---

## Step 3 — Validate OTP

```python
from xpresspay import OtpValidationRequest

validated = client.cards.validate_otp(
    OtpValidationRequest(
        public_key=client.public_key,
        transaction_id="ORDER-001",
        otp="123456",
        payment_type="CARD",
    )
)
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `public_key` | `str` | ✓ | Your `XPPUBK-…` key |
| `transaction_id` | `str` | ✓ | Same ID used in initiate |
| `otp` | `str` | ✓ | OTP entered by the customer |
| `payment_type` | `str` | ✓ | Must be `"CARD"` |

---

## Step 4 — Verify server-side

!!! danger "Always verify before fulfilling an order"
    Never trust the client side. Always confirm the payment server-side
    before delivering goods or services.

```python
from xpresspay import PaymentQueryRequest

result = client.cards.query(
    PaymentQueryRequest(
        public_key=client.public_key,
        transaction_id="ORDER-001",
        payment_type="CARD",
    )
)

if result.is_successful and result.amount == "5000":
    # Safe to fulfill the order
    print("Confirmed:", result.transaction_reference)
else:
    print("Not settled:", result.raw)
```

### PaymentResponse properties

| Property | Type | Description |
|----------|------|-------------|
| `is_successful` | `bool` | `paymentResponseCode == "000"` |
| `requires_validation` | `bool` | OTP/PIN step still pending |
| `suggested_authentication` | `str \| None` | `"PIN"`, `"AVS_VBVSECURECODE"`, or `None` |
| `auth_url` | `str \| None` | 3DSecure iframe URL |
| `transaction_reference` | `str \| None` | Xpresspay's reference |
| `unique_key` | `str \| None` | Xpresspay's unique payment key |
| `amount` | `str \| None` | Original amount |
| `charged_amount` | `str \| None` | Amount actually charged (may include fees) |
| `payment_type` | `str \| None` | `"CARD"` |
| `validation_instruction` | `str \| None` | Human-readable next-step message |
| `raw` | `dict` | Full JSON response for unlisted fields |

---

## Complete example

```python
import os
from xpresspay import (
    XpressPay,
    CardPaymentRequest,
    CardPinAuthRequest,
    OtpValidationRequest,
    PaymentQueryRequest,
    AuthenticationError,
    ValidationError,
    NetworkError,
)

client = XpressPay(
    public_key=os.environ["XPRESSPAY_PUBLIC_KEY"],
    secret_key=os.environ["XPRESSPAY_SECRET_KEY"],
    sandbox=True,
)

try:
    # 1 — Initiate
    resp = client.cards.initiate(
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

    # 2 — Authenticate
    if resp.suggested_authentication == "PIN":
        pin = input("Enter card PIN: ")
        client.cards.authenticate_pin(
            CardPinAuthRequest(
                public_key=client.public_key,
                transaction_id="ORDER-001",
                pin=pin,
            )
        )

    # 3 — Validate OTP
    otp = input("Enter OTP: ")
    client.cards.validate_otp(
        OtpValidationRequest(
            public_key=client.public_key,
            transaction_id="ORDER-001",
            otp=otp,
            payment_type="CARD",
        )
    )

    # 4 — Verify
    result = client.cards.query(
        PaymentQueryRequest(
            public_key=client.public_key,
            transaction_id="ORDER-001",
            payment_type="CARD",
        )
    )

    if result.is_successful:
        print("Payment confirmed:", result.transaction_reference)

except ValidationError as e:
    print("Bad request:", e.message)
except AuthenticationError:
    print("Check your API keys")
except NetworkError:
    print("Network issue — safe to retry")

finally:
    client.close()
```
