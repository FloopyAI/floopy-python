"""``FloopyError`` hierarchy. One subclass per failure mode the gateway can
signal, plus transport-level timeout/connection errors. Mirrors
``src/errors.ts``.

Errors raised by ``chat.completions``/``embeddings``/``models`` come from the
underlying ``openai`` SDK (``openai.APIError`` and friends), *not* this module.
"""

from __future__ import annotations

from typing import Any

FloopyErrorBody = dict[str, Any]


class FloopyError(Exception):
    """Base class for every error raised by Floopy-only resources."""

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        code: str | None = None,
        request_id: str | None = None,
        body: FloopyErrorBody | str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.request_id = request_id
        self.body = body

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


class FloopyAuthError(FloopyError):
    def __init__(self, message: str = "Authentication failed", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class FloopyPlanError(FloopyError):
    """Raised on HTTP 403 when the response carries a ``feature`` field — the
    current plan does not include the requested capability."""

    def __init__(
        self,
        message: str = "Plan does not allow this feature",
        *,
        feature: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.feature = feature


class FloopyRateLimitError(FloopyError):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after_seconds: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after_seconds = retry_after_seconds


class FloopyValidationError(FloopyError):
    def __init__(self, message: str = "Invalid request", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class FloopyNotFoundError(FloopyError):
    def __init__(self, message: str = "Not found", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class FloopyConflictError(FloopyError):
    def __init__(self, message: str = "Conflict", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class FloopyServerError(FloopyError):
    def __init__(self, message: str = "Floopy gateway error", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class FloopyTimeoutError(FloopyError):
    def __init__(self, message: str, cause: BaseException | None = None) -> None:
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause


class FloopyConnectionError(FloopyError):
    def __init__(self, message: str, cause: BaseException | None = None) -> None:
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause


def error_from_status(
    *,
    status: int,
    body: FloopyErrorBody | str | None,
    request_id: str | None,
) -> FloopyError:
    """Map an HTTP status + parsed error body to the right ``FloopyError``.

    The gateway returns ``{"error": {"code", "message", "feature"}}``; a
    plain-text body is preserved on ``.body`` and surfaced generically.
    """
    err_obj = body.get("error") if isinstance(body, dict) else None
    err_obj = err_obj if isinstance(err_obj, dict) else None
    message = (err_obj.get("message") if err_obj else None) or f"HTTP {status}"
    code = err_obj.get("code") if err_obj else None
    feature = err_obj.get("feature") if err_obj else None
    common: dict[str, Any] = {
        "status": status,
        "code": code,
        "request_id": request_id,
        "body": body,
    }

    if status == 400:
        return FloopyValidationError(message, **common)
    if status == 401:
        return FloopyAuthError(message, **common)
    if status == 403:
        if feature is not None:
            return FloopyPlanError(message, feature=feature, **common)
        return FloopyAuthError(message, **common)
    if status == 404:
        return FloopyNotFoundError(message, **common)
    if status == 409:
        return FloopyConflictError(message, **common)
    if status == 429:
        return FloopyRateLimitError(message, **common)
    if status >= 500:
        return FloopyServerError(message, **common)
    return FloopyError(message, **common)
