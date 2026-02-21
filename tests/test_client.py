"""Tests for the XpressPay client initialisation and configuration."""

from __future__ import annotations

import pytest

from xpresspay import XpressPay

VALID_PUBLIC_KEY = "XPPUBK-ead4d14d9ded04aer5d5b63a0a06d2f-X"
VALID_SECRET_KEY = "XPSECK-ab12cd34ef56gh78ij90kl12mnop-X"


class TestClientInit:
    def test_sandbox_mode_by_default(self) -> None:
        client = XpressPay(VALID_PUBLIC_KEY, VALID_SECRET_KEY)
        assert client.is_sandbox is True
        client.close()

    def test_live_mode(self) -> None:
        client = XpressPay(VALID_PUBLIC_KEY, VALID_SECRET_KEY, sandbox=False)
        assert client.is_sandbox is False
        client.close()

    def test_public_key_property(self) -> None:
        client = XpressPay(VALID_PUBLIC_KEY, VALID_SECRET_KEY)
        assert client.public_key == VALID_PUBLIC_KEY
        client.close()

    def test_repr_does_not_expose_secret_key(self) -> None:
        client = XpressPay(VALID_PUBLIC_KEY, VALID_SECRET_KEY)
        r = repr(client)
        assert VALID_SECRET_KEY not in r
        assert "XPSECK" not in r
        client.close()

    def test_invalid_public_key_raises(self) -> None:
        with pytest.raises(ValueError, match="public_key"):
            XpressPay("invalid-key", VALID_SECRET_KEY)

    def test_invalid_secret_key_raises(self) -> None:
        with pytest.raises(ValueError, match="secret_key"):
            XpressPay(VALID_PUBLIC_KEY, "invalid-secret")

    def test_empty_public_key_raises(self) -> None:
        with pytest.raises(ValueError):
            XpressPay("", VALID_SECRET_KEY)

    def test_empty_secret_key_raises(self) -> None:
        with pytest.raises(ValueError):
            XpressPay(VALID_PUBLIC_KEY, "")

    def test_context_manager(self) -> None:
        with XpressPay(VALID_PUBLIC_KEY, VALID_SECRET_KEY) as client:
            assert client.is_sandbox is True

    def test_resources_are_accessible(self) -> None:
        client = XpressPay(VALID_PUBLIC_KEY, VALID_SECRET_KEY)
        assert client.cards is not None
        assert client.accounts is not None
        assert client.banks is not None
        client.close()
