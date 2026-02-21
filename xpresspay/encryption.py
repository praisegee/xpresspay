"""
3DES-24 encryption for Xpresspay API payloads.

Xpresspay requires all payment requests to be encrypted with Triple DES (3DES)
in ECB mode using PKCS5/PKCS7 padding before transmission. The 24-byte key is
derived from your secret key via MD5 hashing.

The secret key NEVER leaves your server — only the encrypted ciphertext is sent.
"""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from Crypto.Cipher import DES3

from .exceptions import EncryptionError

_PREFIX = "XPSECK-"


def _derive_key(secret_key: str) -> bytes:
    """
    Derive the 24-byte 3DES key from the Xpresspay secret key.

    Algorithm (as documented by Xpresspay):
    1. Strip the "XPSECK-" prefix and take the first 12 characters.
    2. MD5-hash the full (un-stripped) secret key and take the last 12 hex chars.
    3. Concatenate both parts → 24-byte key.
    """
    if not secret_key:
        raise EncryptionError("Secret key must not be empty.")

    stripped = secret_key.replace(_PREFIX, "")
    if len(stripped) < 12:
        raise EncryptionError(
            "Secret key is too short to derive an encryption key. "
            "Ensure you are using the full key from your Xpresspay dashboard."
        )

    part_a = stripped[:12]

    md5_hex = hashlib.md5(secret_key.encode("utf-8")).hexdigest()
    part_b = md5_hex[-12:]

    combined = part_a + part_b  # 24 ASCII chars → 24 bytes when encoded as UTF-8
    return combined.encode("utf-8")


def encrypt_payload(data: dict[str, Any], secret_key: str) -> str:
    """
    Encrypt a dictionary payload with 3DES-ECB and return a Base64-encoded string.

    Args:
        data: The request fields to encrypt (e.g., card/account details).
        secret_key: Your Xpresspay secret key (kept server-side only).

    Returns:
        Base64-encoded encrypted string to be sent as the ``request`` field.

    Raises:
        EncryptionError: If key derivation or encryption fails.
    """
    try:
        plaintext = json.dumps(data, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise EncryptionError(f"Failed to serialize payload to JSON: {exc}") from exc

    try:
        key = _derive_key(secret_key)
        # PKCS7 padding to a multiple of 8 bytes (DES block size)
        pad_len = 8 - (len(plaintext.encode("utf-8")) % 8)
        padded = plaintext + chr(pad_len) * pad_len

        cipher = DES3.new(key, DES3.MODE_ECB)
        encrypted_bytes = cipher.encrypt(padded.encode("utf-8"))
        return base64.b64encode(encrypted_bytes).decode("utf-8")
    except Exception as exc:
        raise EncryptionError(f"Encryption failed: {exc}") from exc
