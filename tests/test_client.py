"""Tests for the XpressPay client initialisation and configuration."""

from __future__ import annotations

import pytest

from xpresspay import XpressPay

VALID_PUBLIC_KEY = "XPPUBK-ead4d14d9ded04aer5d5b63a0a06d2f-X"


class TestClientInit:
    def test_sandbox_mode_by_default(self) -> None:
        client = XpressPay(VALID_PUBLIC_KEY)
        assert client.is_sandbox is True
        client.close()

    def test_live_mode(self) -> None:
        client = XpressPay(VALID_PUBLIC_KEY, sandbox=False)
        assert client.is_sandbox is False
        client.close()

    def test_public_key_property(self) -> None:
        client = XpressPay(VALID_PUBLIC_KEY)
        assert client.public_key == VALID_PUBLIC_KEY
        client.close()

    def test_invalid_public_key_raises(self) -> None:
        with pytest.raises(ValueError, match="public_key"):
            XpressPay("invalid-key")

    def test_empty_public_key_raises(self) -> None:
        with pytest.raises(ValueError):
            XpressPay("")

    def test_context_manager(self) -> None:
        with XpressPay(VALID_PUBLIC_KEY) as client:
            assert client.is_sandbox is True

    def test_payments_resource_is_accessible(self) -> None:
        client = XpressPay(VALID_PUBLIC_KEY)
        assert client.payments is not None
        client.close()

    def test_repr(self) -> None:
        client = XpressPay(VALID_PUBLIC_KEY)
        r = repr(client)
        assert VALID_PUBLIC_KEY in r
        assert "sandbox" in r
        client.close()
