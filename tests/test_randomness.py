"""Tests for secure random material boundaries and recovery-key formatting."""

import pytest

from app.security.randomness import (
    AES_GCM_NONCE_BYTES,
    RECOVERY_KEY_LENGTH,
    VAULT_KEY_BYTES,
    decode_recovery_key,
    generate_aes_gcm_nonce,
    generate_recovery_key,
    generate_vault_key,
    secure_random_bytes,
)


def test_secure_random_bytes_validates_length():
    assert len(secure_random_bytes(32)) == 32

    with pytest.raises(ValueError):
        secure_random_bytes(0)
    with pytest.raises(ValueError):
        secure_random_bytes(-1)
    with pytest.raises(TypeError):
        secure_random_bytes("32")


def test_key_and_nonce_sizes_match_approved_parameters():
    assert len(generate_vault_key()) == VAULT_KEY_BYTES == 32
    assert len(generate_aes_gcm_nonce()) == AES_GCM_NONCE_BYTES == 12


def test_recovery_key_is_16_alphanumeric_characters():
    recovery_key = generate_recovery_key()

    assert len(recovery_key) == RECOVERY_KEY_LENGTH == 16
    assert recovery_key.isalnum()
    assert len(decode_recovery_key(recovery_key)) == RECOVERY_KEY_LENGTH


def test_recovery_key_rejects_invalid_input():
    with pytest.raises(ValueError):
        decode_recovery_key("not-a-valid-key")
    with pytest.raises(ValueError):
        decode_recovery_key("0" * 15)
