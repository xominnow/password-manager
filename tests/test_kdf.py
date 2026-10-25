"""Tests for the Scrypt key-derivation boundary."""

import pytest

from app.security.kdf import (
    DEFAULT_SCRYPT_PARAMETERS,
    ScryptParameters,
    derive_key,
    derive_password_key,
    derive_recovery_key,
    generate_kdf_salt,
)
from app.security.randomness import generate_recovery_key as generate_recovery_key_text
from app.security.randomness import decode_recovery_key


def test_default_parameters_match_approved_scrypt_baseline():
    parameters = DEFAULT_SCRYPT_PARAMETERS

    assert parameters.algorithm == "scrypt"
    assert parameters.n == 65_536
    assert parameters.r == 8
    assert parameters.p == 1
    assert parameters.salt_length == 16
    assert parameters.output_length == 32


def test_derivation_is_deterministic_for_same_secret_and_salt():
    salt = generate_kdf_salt()

    first = derive_password_key("Correct Horse Battery Staple", salt)
    second = derive_password_key("Correct Horse Battery Staple", salt)

    assert first == second
    assert len(first) == 32


def test_different_salts_produce_different_keys():
    first_salt = generate_kdf_salt()
    second_salt = generate_kdf_salt()

    assert derive_key(b"test secret", first_salt) != derive_key(b"test secret", second_salt)


def test_recovery_key_derivation_accepts_new_canonical_input():
    recovery_key = decode_recovery_key(generate_recovery_key_text())
    derived = derive_recovery_key(recovery_key, generate_kdf_salt())

    assert len(derived) == 32


def test_weaker_parameters_and_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        derive_key(
            b"secret",
            generate_kdf_salt(),
            ScryptParameters(n=32_768),
        )
    with pytest.raises(ValueError):
        derive_key(b"secret", generate_kdf_salt(), ScryptParameters(n=65_535))
    with pytest.raises(ValueError):
        derive_key(b"secret", b"short salt")
    with pytest.raises(ValueError):
        derive_key(b"", generate_kdf_salt())
    with pytest.raises(ValueError):
        derive_recovery_key(b"short", generate_kdf_salt())
