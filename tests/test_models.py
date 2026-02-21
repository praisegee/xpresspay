"""Tests for request/response model helpers."""

from __future__ import annotations

from xpresspay.models import (
    InitializeRequest,
    InitializeResponse,
    VerifyRequest,
    VerifyResponse,
)


class TestInitializeRequest:
    def _make(self) -> InitializeRequest:
        return InitializeRequest(
            amount="1000.00",
            email="customer@example.com",
            transaction_id="ORDER-001",
        )

    def test_required_fields_in_dict(self) -> None:
        d = self._make().to_dict()
        assert d["amount"] == "1000.00"
        assert d["email"] == "customer@example.com"
        assert d["transactionId"] == "ORDER-001"
        assert d["currency"] == "NGN"

    def test_defaults(self) -> None:
        d = self._make().to_dict()
        assert d["isApiUser"] is True
        assert d["isSplitpayment"] is False
        assert d["isRecurring"] is False
        assert d["applyConviniencyCharge"] is False

    def test_optional_fields_omitted_when_none(self) -> None:
        d = self._make().to_dict()
        assert "productId" not in d
        assert "callBackUrl" not in d
        assert "metadata" not in d

    def test_optional_fields_included_when_set(self) -> None:
        req = self._make()
        req.callback_url = "https://example.com/callback"
        req.product_id = "PROD-1"
        req.metadata = [{"name": "orderId", "value": "123"}]
        d = req.to_dict()
        assert d["callBackUrl"] == "https://example.com/callback"
        assert d["productId"] == "PROD-1"
        assert d["metadata"] == [{"name": "orderId", "value": "123"}]


class TestInitializeResponse:
    def test_is_successful_true(self) -> None:
        resp = InitializeResponse(
            response_code="00",
            response_message="Successfully initialized payment",
            payment_url="https://xpay.com/abc123",
            reference="abc123",
            raw={},
        )
        assert resp.is_successful is True

    def test_is_successful_false(self) -> None:
        resp = InitializeResponse(
            response_code="99",
            response_message="Failed",
            payment_url=None,
            reference=None,
            raw={},
        )
        assert resp.is_successful is False


class TestVerifyRequest:
    def test_to_dict(self) -> None:
        req = VerifyRequest(transaction_id="ORDER-001")
        assert req.to_dict() == {"transactionId": "ORDER-001"}


class TestVerifyResponse:
    def _make_raw(self, is_successful: object = "true") -> dict:
        return {
            "responseCode": "00",
            "responseMessage": "Payment successful",
            "data": {
                "amount": "1000.00",
                "currency": "NGN",
                "status": "Transaction Successful",
                "isSuccessful": is_successful,
                "paymentType": "Card",
                "gatewayResponse": "Transaction Successful. Approved",
                "transactionId": "ORDER-001",
            },
        }

    def test_is_successful_string_true(self) -> None:
        resp = VerifyResponse("00", "Payment successful", self._make_raw("true"))
        assert resp.is_successful is True

    def test_is_successful_bool_true(self) -> None:
        resp = VerifyResponse("00", "Payment successful", self._make_raw(True))
        assert resp.is_successful is True

    def test_is_successful_false(self) -> None:
        resp = VerifyResponse("00", "Failed", self._make_raw("false"))
        assert resp.is_successful is False

    def test_amount_property(self) -> None:
        resp = VerifyResponse("00", "", self._make_raw())
        assert resp.amount == "1000.00"

    def test_payment_type_property(self) -> None:
        resp = VerifyResponse("00", "", self._make_raw())
        assert resp.payment_type == "Card"

    def test_missing_data_returns_none(self) -> None:
        resp = VerifyResponse("00", "", {})
        assert resp.amount is None
        assert resp.status is None
        assert resp.is_successful is False
