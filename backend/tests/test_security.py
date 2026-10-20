"""
Tests for password hashing and its input limits.

bcrypt accepts at most 72 BYTES of input. The registration schema
previously allowed 100 CHARACTERS, so a long passphrase reached bcrypt,
raised, and surfaced as an unhandled 500 on the registration endpoint.
These tests pin down the byte-level boundary at both layers.
"""

import pydantic
import pytest

from app.core.security import (
    BCRYPT_MAX_PASSWORD_BYTES,
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
    get_current_user_id,
)
from app.schemas.user import UserCreate


class TestPasswordHashing:

    def test_hash_then_verify_roundtrip(self):
        h = get_password_hash("Demo@12345")
        assert verify_password("Demo@12345", h)

    def test_wrong_password_rejected(self):
        h = get_password_hash("Demo@12345")
        assert not verify_password("wrong", h)

    def test_hash_is_salted(self):
        """Same input must not produce the same hash twice."""
        assert get_password_hash("samePassword1") != get_password_hash("samePassword1")

    def test_hash_is_bcrypt_cost_12(self):
        assert get_password_hash("whatever1").startswith("$2b$12$")

    def test_password_at_the_byte_limit_is_accepted(self):
        pw = "A" * BCRYPT_MAX_PASSWORD_BYTES
        assert verify_password(pw, get_password_hash(pw))

    def test_password_over_the_byte_limit_raises_clearly(self):
        """A ValueError here, not bcrypt's own error leaking as a 500."""
        with pytest.raises(ValueError, match="exceeds bcrypt"):
            get_password_hash("A" * (BCRYPT_MAX_PASSWORD_BYTES + 1))

    def test_multibyte_password_measured_in_bytes_not_characters(self):
        """
        41 accented characters are 81 UTF-8 bytes — under any character
        cap of 72, but over bcrypt's byte limit.
        """
        pw = "e" + "é" * 40
        assert len(pw) <= BCRYPT_MAX_PASSWORD_BYTES
        assert len(pw.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES

        with pytest.raises(ValueError, match="exceeds bcrypt"):
            get_password_hash(pw)


class TestRegistrationSchema:

    def test_valid_password_accepted(self):
        user = UserCreate(email="a@b.com", password="GoodPass123", full_name="Test User")
        assert user.password == "GoodPass123"

    def test_too_short_rejected(self):
        with pytest.raises(pydantic.ValidationError):
            UserCreate(email="a@b.com", password="short", full_name="Test User")

    def test_over_byte_limit_rejected_by_schema(self):
        """Caught as a 422 at the edge rather than a 500 in the hasher."""
        with pytest.raises(pydantic.ValidationError):
            UserCreate(
                email="a@b.com",
                password="A" * (BCRYPT_MAX_PASSWORD_BYTES + 1),
                full_name="Test User",
            )

    def test_multibyte_over_byte_limit_rejected_by_schema(self):
        with pytest.raises(pydantic.ValidationError, match="72 bytes"):
            UserCreate(
                email="a@b.com",
                password="e" + "é" * 40,
                full_name="Test User",
            )

    def test_invalid_email_rejected(self):
        with pytest.raises(pydantic.ValidationError):
            UserCreate(email="not-an-email", password="GoodPass123", full_name="Test User")


class TestTokens:

    def test_token_roundtrip_yields_the_subject(self):
        token = create_access_token({"sub": "42"})
        assert get_current_user_id(token) == 42

    def test_token_carries_access_type(self):
        assert decode_token(create_access_token({"sub": "1"}))["type"] == "access"

    def test_garbage_token_returns_none(self):
        assert decode_token("not.a.token") is None
        assert get_current_user_id("not.a.token") is None

    def test_token_signed_with_another_key_is_rejected(self):
        """Guards against accepting tokens this server did not issue."""
        from jose import jwt
        forged = jwt.encode({"sub": "1", "type": "access"}, "a-different-key", algorithm="HS256")
        assert decode_token(forged) is None


class TestNoPlainTextFallback:
    """
    Verification must have exactly one path: bcrypt.

    An earlier version compared the strings directly when bcrypt raised,
    to support dev accounts predating hashing. That turned any non-hash
    value written into `password_hash` into a working password.
    """

    def test_a_plaintext_stored_value_never_authenticates(self):
        from app.core.security import verify_password

        assert verify_password("hunter2", "hunter2") is False

    def test_an_empty_stored_hash_never_authenticates(self):
        from app.core.security import verify_password

        assert verify_password("", "") is False
        assert verify_password("anything", "") is False

    def test_a_corrupt_hash_fails_closed_rather_than_raising(self):
        from app.core.security import verify_password

        for corrupt in ("not-a-hash", "$2b$12$tooshort", "$$$$", "null"):
            assert verify_password("password", corrupt) is False

    def test_a_real_bcrypt_hash_still_verifies(self):
        from app.core.security import get_password_hash, verify_password

        hashed = get_password_hash("Correct@123")
        assert verify_password("Correct@123", hashed) is True
        assert verify_password("Wrong@123", hashed) is False
