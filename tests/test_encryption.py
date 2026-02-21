"""Tests for the 3DES encryption module."""

from __future__ import annotations

import base64

import pytest

from xpresspay.encryption import _derive_key, encrypt_payload
from xpresspay.exceptions import EncryptionError

# A realistic-looking test secret key (same format as real keys)
TEST_SECRET_KEY = "XPSECK-ab12cd34ef56gh78ij90kl12-X"


class TestDeriveKey:
    def test_returns_24_bytes(self) -> None:
        key = _derive_key(TEST_SECRET_KEY)
        assert len(key) == 24

    def test_deterministic(self) -> None:
        assert _derive_key(TEST_SECRET_KEY) == _derive_key(TEST_SECRET_KEY)

    def test_different_keys_produce_different_results(self) -> None:
        key_a = _derive_key("XPSECK-aaaaaaaaaaaaaaaaaaaaaaaa-X")
        key_b = _derive_key("XPSECK-bbbbbbbbbbbbbbbbbbbbbbbb-X")
        assert key_a != key_b

    def test_empty_key_raises(self) -> None:
        with pytest.raises(EncryptionError):
            _derive_key("")

    def test_short_key_raises(self) -> None:
        with pytest.raises(EncryptionError):
            _derive_key("XPSECK-short")

    def test_strips_prefix_correctly(self) -> None:
        key_with = _derive_key("XPSECK-ab12cd34ef56gh-X")
        # First 12 chars of stripped key must appear at start of derived key
        stripped = "ab12cd34ef56gh-X".replace("XPSECK-", "")
        assert key_with[:12] == stripped[:12].encode("utf-8")


class TestEncryptPayload:
    def test_returns_base64_string(self) -> None:
        result = encrypt_payload({"amount": "1000"}, TEST_SECRET_KEY)
        # Should be valid base64
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_output_is_multiple_of_8_bytes(self) -> None:
        data = {"amount": "1000", "email": "test@test.com"}
        result = encrypt_payload(data, TEST_SECRET_KEY)
        decoded = base64.b64decode(result)
        assert len(decoded) % 8 == 0

    def test_different_payloads_produce_different_ciphertext(self) -> None:
        ct1 = encrypt_payload({"amount": "1000"}, TEST_SECRET_KEY)
        ct2 = encrypt_payload({"amount": "2000"}, TEST_SECRET_KEY)
        assert ct1 != ct2

    def test_non_serialisable_payload_raises(self) -> None:
        with pytest.raises(EncryptionError, match="serialize"):
            encrypt_payload({"bad": object()}, TEST_SECRET_KEY)  # type: ignore[arg-type]

    def test_empty_dict_encrypts(self) -> None:
        result = encrypt_payload({}, TEST_SECRET_KEY)
        assert isinstance(result, str)
        assert len(result) > 0
