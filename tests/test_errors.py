from __future__ import annotations

from floopy._errors import (
    FloopyAuthError,
    FloopyConflictError,
    FloopyNotFoundError,
    FloopyPlanError,
    FloopyRateLimitError,
    FloopyServerError,
    FloopyValidationError,
    error_from_status,
)


def test_400_validation() -> None:
    err = error_from_status(
        status=400,
        body={"error": {"code": "bad", "message": "missing field"}},
        request_id="req_1",
    )
    assert isinstance(err, FloopyValidationError)
    assert err.message == "missing field"
    assert err.code == "bad"
    assert err.request_id == "req_1"


def test_401_auth() -> None:
    assert isinstance(error_from_status(status=401, body=None, request_id=None), FloopyAuthError)


def test_403_with_feature_plan() -> None:
    err = error_from_status(
        status=403,
        body={"error": {"feature": "audit_api", "message": "Plan does not allow"}},
        request_id=None,
    )
    assert isinstance(err, FloopyPlanError)
    assert err.feature == "audit_api"


def test_403_without_feature_auth() -> None:
    assert isinstance(error_from_status(status=403, body=None, request_id=None), FloopyAuthError)


def test_404_not_found() -> None:
    assert isinstance(
        error_from_status(status=404, body=None, request_id=None), FloopyNotFoundError
    )


def test_409_conflict() -> None:
    assert isinstance(
        error_from_status(status=409, body=None, request_id=None), FloopyConflictError
    )


def test_429_rate_limit() -> None:
    assert isinstance(
        error_from_status(status=429, body=None, request_id=None), FloopyRateLimitError
    )


def test_5xx_server() -> None:
    assert isinstance(error_from_status(status=503, body=None, request_id=None), FloopyServerError)


def test_plaintext_body_preserved() -> None:
    err = error_from_status(status=500, body="upstream exploded", request_id=None)
    assert isinstance(err, FloopyServerError)
    assert err.body == "upstream exploded"
    assert err.message == "HTTP 500"
