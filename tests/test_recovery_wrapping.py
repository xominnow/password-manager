"""Tests for independent recovery-key vault-key wrapping."""

from dataclasses import replace

import pytest

from app.security.keys import create_vault_key
from app.security.randomness import decode_recovery_key, generate_recovery_key
from app.security.wrapping import (
    InvalidRecoveryWrapper,
    RecoveryKeyWrapper,
    unwrap_recovery_key,
    wrap_recovery_key,
)


def _recovery_bytes() -> bytes:
    return decode_recovery_key(generate_recovery_key())


def test_recovery_wrapper_round_trips_the_vault_key():
    vault_key = create_vault_key()
    recovery_key = _recovery_bytes()
    wrapper = wrap_recovery_key(vault_key, recovery_key, "vault-001")

    assert isinstance(wrapper, RecoveryKeyWrapper)
    assert wrapper.purpose == "recovery"
    assert unwrap_recovery_key(wrapper, recovery_key).material == vault_key.material


def test_recovery_wrapper_is_independent_from_master_context():
    vault_key = create_vault_key()
    first_key = _recovery_bytes()
    second_key = _recovery_bytes()
    first = wrap_recovery_key(vault_key, first_key, "vault-001")
    second = wrap_recovery_key(vault_key, second_key, "vault-001")

    assert first.kdf_salt != second.kdf_salt
    assert first.nonce != second.nonce
    with pytest.raises(InvalidRecoveryWrapper):
        unwrap_recovery_key(first, second_key)


def test_wrong_context_or_ciphertext_fails_generically():
    recovery_key = _recovery_bytes()
    wrapper = wrap_recovery_key(create_vault_key(), recovery_key, "vault-001")

    with pytest.raises(InvalidRecoveryWrapper):
        unwrap_recovery_key(replace(wrapper, vault_id="different-vault"), recovery_key)

    tampered = replace(wrapper, ciphertext=wrapper.ciphertext[:-1] + bytes([wrapper.ciphertext[-1] ^ 1]))
    with pytest.raises(InvalidRecoveryWrapper):
        unwrap_recovery_key(tampered, recovery_key)


def test_recovery_wrapper_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        wrap_recovery_key(create_vault_key(), b"short", "vault-001")
