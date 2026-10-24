"""Tests for AES-256-GCM authenticated encryption."""

from dataclasses import replace

import pytest

from app.security.aead import (
    AES_GCM_KEY_BYTES,
    AES_GCM_TAG_BYTES,
    EncryptedPayload,
    InvalidCiphertext,
    decrypt_bytes,
    encrypt_bytes,
)
from app.security.randomness import generate_vault_key


AAD = b"lockbox|v1|record|record-001"


def test_encrypt_decrypt_round_trip():
    key = generate_vault_key()
    plaintext = b"encrypted credential payload"

    payload = encrypt_bytes(key, plaintext, AAD)

    assert len(payload.nonce) == 12
    assert len(payload.ciphertext) == len(plaintext) + AES_GCM_TAG_BYTES
    assert decrypt_bytes(key, payload, AAD) == plaintext


def test_each_encryption_uses_a_fresh_nonce():
    key = generate_vault_key()
    first = encrypt_bytes(key, b"same plaintext", AAD)
    second = encrypt_bytes(key, b"same plaintext", AAD)

    assert first.nonce != second.nonce
    assert first.ciphertext != second.ciphertext


def test_changed_context_key_or_ciphertext_fails_authentication():
    key = generate_vault_key()
    payload = encrypt_bytes(key, b"secret", AAD)

    with pytest.raises(InvalidCiphertext):
        decrypt_bytes(key, payload, b"lockbox|v1|record|different")
    with pytest.raises(InvalidCiphertext):
        decrypt_bytes(generate_vault_key(), payload, AAD)

    tampered = replace(payload, ciphertext=payload.ciphertext[:-1] + bytes([payload.ciphertext[-1] ^ 1]))
    with pytest.raises(InvalidCiphertext):
        decrypt_bytes(key, tampered, AAD)


def test_aead_rejects_invalid_parameters():
    with pytest.raises(ValueError):
        encrypt_bytes(b"short", b"plaintext", AAD)
    with pytest.raises(ValueError):
        encrypt_bytes(b"A" * AES_GCM_KEY_BYTES, b"plaintext", b"")
    with pytest.raises(ValueError):
        EncryptedPayload(nonce=b"short", ciphertext=b"ciphertext")
    with pytest.raises(ValueError):
        EncryptedPayload(nonce=b"A" * 12, ciphertext=b"short")
