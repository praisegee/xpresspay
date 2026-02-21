"""Tests for request/response model helpers."""

from __future__ import annotations

from xpresspay.models import (
    AccountPaymentRequest,
    CardAvsAuthRequest,
    CardPaymentRequest,
    CardPinAuthRequest,
    OtpValidationRequest,
    PaymentQueryRequest,
    PaymentResponse,
)

PUBLIC_KEY = "XPPUBK-ead4d14d9ded04aer5d5b63a0a06d2f-X"


class TestCardPaymentRequest:
    def _make(self) -> CardPaymentRequest:
        return CardPaymentRequest(
            public_key=PUBLIC_KEY,
            card_number="5438898014560229",
            cvv="789",
            expiry_month="09",
            expiry_year="25",
            amount="5000",
            email="customer@example.com",
            transaction_id="TXN-001",
        )

    def test_required_fields_in_dict(self) -> None:
        d = self._make().to_encrypt_dict()
        assert d["publicKey"] == PUBLIC_KEY
        assert d["cardNumber"] == "5438898014560229"
        assert d["paymentType"] == "CARD"
        assert d["currency"] == "NGN"

    def test_optional_fields_omitted_when_none(self) -> None:
        d = self._make().to_encrypt_dict()
        assert "phoneNumber" not in d
        assert "billingZip" not in d
        assert "meta" not in d

    def test_optional_fields_included_when_set(self) -> None:
        req = self._make()
        req.phone_number = "08012345678"
        req.billing_zip = "07205"
        req.meta = [{"metaName": "orderId", "metaValue": "123"}]
        d = req.to_encrypt_dict()
        assert d["phoneNumber"] == "08012345678"
        assert d["billingZip"] == "07205"
        assert d["meta"] == [{"metaName": "orderId", "metaValue": "123"}]


class TestAccountPaymentRequest:
    def _make(self) -> AccountPaymentRequest:
        return AccountPaymentRequest(
            public_key=PUBLIC_KEY,
            account_number="0690000031",
            bank_code="044",
            amount="10000",
            email="customer@example.com",
            transaction_id="TXN-002",
        )

    def test_required_fields_in_dict(self) -> None:
        d = self._make().to_encrypt_dict()
        assert d["accountNumber"] == "0690000031"
        assert d["bankCode"] == "044"
        assert d["paymentType"] == "ACCOUNT"

    def test_bank_specific_fields_omitted_by_default(self) -> None:
        d = self._make().to_encrypt_dict()
        assert "dateOfBirth" not in d
        assert "bvn" not in d
        assert "redirectUrl" not in d

    def test_bank_specific_fields_included(self) -> None:
        req = self._make()
        req.date_of_birth = "01011990"
        req.bvn = "12345678901"
        d = req.to_encrypt_dict()
        assert d["dateOfBirth"] == "01011990"
        assert d["bvn"] == "12345678901"


class TestCardPinAuthRequest:
    def test_to_dict(self) -> None:
        req = CardPinAuthRequest(
            public_key=PUBLIC_KEY, transaction_id="TXN-001", pin="1234"
        )
        d = req.to_dict()
        assert d["suggestedAuthentication"] == "PIN"
        assert d["pin"] == "1234"
        assert d["paymentType"] == "CARD"


class TestCardAvsAuthRequest:
    def test_to_dict_with_billing(self) -> None:
        req = CardAvsAuthRequest(
            public_key=PUBLIC_KEY,
            transaction_id="TXN-001",
            billing_city="Lagos",
            billing_country="NG",
        )
        d = req.to_dict()
        assert d["suggestedAuthentication"] == "AVS_VBVSECURECODE"
        assert d["billingCity"] == "Lagos"
        assert "billingZip" not in d

    def test_to_dict_omits_none_fields(self) -> None:
        req = CardAvsAuthRequest(public_key=PUBLIC_KEY, transaction_id="TXN-001")
        d = req.to_dict()
        assert "billingCity" not in d


class TestPaymentQueryRequest:
    def test_to_dict(self) -> None:
        req = PaymentQueryRequest(
            public_key=PUBLIC_KEY,
            transaction_id="TXN-001",
            payment_type="CARD",
        )
        d = req.to_dict()
        assert d["transactionId"] == "TXN-001"
        assert d["paymentType"] == "CARD"


class TestOtpValidationRequest:
    def test_to_dict(self) -> None:
        req = OtpValidationRequest(
            public_key=PUBLIC_KEY,
            transaction_id="TXN-001",
            otp="123456",
            payment_type="ACCOUNT",
        )
        d = req.to_dict()
        assert d["otp"] == "123456"
        assert d["paymentType"] == "ACCOUNT"
        assert d["transactionReference"] == "TXN-001"


class TestPaymentResponse:
    def _make_raw(
        self,
        payment_response_code: str = "000",
        auth_code: str = "00",
        suggested: str | None = None,
    ) -> dict:
        payment: dict = {
            "paymentResponseCode": payment_response_code,
            "authenticatePaymentResponseCode": auth_code,
            "amount": "5000",
            "chargedAmount": "5050",
            "paymentType": "CARD",
            "transactionReference": "REF-001",
            "uniqueKey": "UKEY-001",
        }
        if suggested:
            payment["suggestedAuthentication"] = suggested
        return {
            "status": "SUCCESS",
            "message": "Successful",
            "data": {"payment": payment},
        }

    def test_is_successful_true(self) -> None:
        resp = PaymentResponse("SUCCESS", "Successful", self._make_raw("000"))
        assert resp.is_successful is True

    def test_is_successful_false(self) -> None:
        resp = PaymentResponse("PENDING", "", self._make_raw("099"))
        assert resp.is_successful is False

    def test_requires_validation_true(self) -> None:
        resp = PaymentResponse("SUCCESS", "", self._make_raw(auth_code="02"))
        assert resp.requires_validation is True

    def test_suggested_authentication(self) -> None:
        resp = PaymentResponse(
            "SUCCESS", "", self._make_raw(suggested="PIN", auth_code="02")
        )
        assert resp.suggested_authentication == "PIN"

    def test_amount_property(self) -> None:
        resp = PaymentResponse("SUCCESS", "", self._make_raw())
        assert resp.amount == "5000"
        assert resp.charged_amount == "5050"

    def test_missing_data_returns_none(self) -> None:
        resp = PaymentResponse("SUCCESS", "", {})
        assert resp.amount is None
        assert resp.auth_url is None
        assert resp.is_successful is False
