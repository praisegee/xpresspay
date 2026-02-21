"""Custom exceptions for the xpresspay SDK."""

from __future__ import annotations


class XpressPayError(Exception):
    """Base exception for all xpresspay SDK errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        return f"{cls}(message={self.message!r}, status_code={self.status_code!r})"


class AuthenticationError(XpressPayError):
    """Raised when API key authentication fails (HTTP 401)."""


class ValidationError(XpressPayError):
    """Raised when request data fails validation (HTTP 400)."""

    def __init__(
        self,
        message: str,
        error_type: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message, status_code)
        self.error_type = error_type


class NotFoundError(XpressPayError):
    """Raised when a requested resource is not found (HTTP 404)."""


class ProcessingError(XpressPayError):
    """Raised when a server-side processing error occurs (HTTP 5xx)."""


class EncryptionError(XpressPayError):
    """Raised when payload encryption fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=None)


class NetworkError(XpressPayError):
    """Raised when a network-level error occurs (timeout, connection refused, etc.)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=None)
