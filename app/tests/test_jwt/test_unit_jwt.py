import pytest
from datetime import UTC, datetime, timedelta
from app.utils.jwt import create_access_token, decode_access_token, create_refresh_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


def test_create_and_decode_access_token():
    data = {"sub": "user@example.com"}
    token = create_access_token(data)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == data["sub"]
    assert "exp" in payload


def test_create_access_token_with_custom_expiration():
    data = {"sub": "user@example.com"}
    expires = timedelta(minutes=1)

    token = create_access_token(data, expires_delta=expires)
    payload = decode_access_token(token)

    exp_time = datetime.fromtimestamp(payload["exp"], UTC)
    now = datetime.now(UTC)
    assert (
        now + expires - timedelta(seconds=2)
        <= exp_time
        <= now + expires + timedelta(seconds=2)
    )


def test_decode_access_token_invalid_token():
    invalid_token = "invalid.token.value"
    payload = decode_access_token(invalid_token)
    assert payload is None


def test_create_refresh_token():
    data = {"sub": "refresh@example.com"}
    token = create_refresh_token(data)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == data["sub"]
    assert "exp" in payload


def test_refresh_token_expiration():
    data = {"sub": "refresh@example.com"}
    token = create_refresh_token(data)
    payload = decode_access_token(token)

    exp_time = datetime.fromtimestamp(payload["exp"], UTC)
    now = datetime.now(UTC)
    expected_exp = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    assert now <= exp_time <= expected_exp + timedelta(seconds=2)
