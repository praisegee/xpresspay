"""
Banks list resource.

Retrieves the list of supported Nigerian banks and their codes.
The bank code is required when initiating an account payment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .._http import HttpClient


@dataclass
class Bank:
    """A supported bank with its name and code."""

    name: str
    code: str
    raw: dict[str, Any]


class BanksResource:
    """Fetches available banks from the Xpresspay API."""

    def __init__(self, public_key: str, http: HttpClient, base_url: str) -> None:
        self._public_key = public_key
        self._http = http
        self._base = base_url.rstrip("/")

    def list(self) -> list[Bank]:
        """
        Return all banks supported for account payments.

        Returns:
            A list of :class:`Bank` objects.

        Example::

            banks = client.banks.list()
            for bank in banks:
                print(bank.name, bank.code)
        """
        raw = self._http.get(
            f"{self._base}/v1/banks",
            params={"publicKey": self._public_key},
        )
        raw_inner = raw.get("data", raw) if isinstance(raw, dict) else raw
        banks_data: list[dict[str, Any]] = raw_inner
        if isinstance(banks_data, dict):
            banks_data = banks_data.get("banks", [])

        result: list[Bank] = []
        for entry in banks_data:
            result.append(
                Bank(
                    name=entry.get("name", entry.get("bankName", "")),
                    code=entry.get("code", entry.get("bankCode", "")),
                    raw=entry,
                )
            )
        return result
