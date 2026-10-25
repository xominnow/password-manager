"""Tests for master-password vault-key wrapping."""

from dataclasses import replace

import pytest

from app.security.keys import create_vault_key
from app.security.wrapping import (
    AES_GCM_TAG_BYTES,
    InvalidMasterWrapper,
    MasterKeyWrapper,
    unwrap_master_key,
    wrap_master_key,
)


PASSWORD = "Correct Horse Battery Staple"


def test_master_wrapper_round_trips_the_vault_key():
    vault_key = create_vault_key()
    wrapper = wrap_master_key(vault_key, PASSWORD, "vault-001")

    assert isinstance(wrapper, MasterKeyWrapper)
    assert wrapper.purpose == "master"
    assert len(wrapper.ciphertext) == len(vault_key.material) + AES_GCM_TAG_BYTES
    assert unwrap_master_key(wrapper, PASSWORD).material == vault_key.material


def test_each_master_wrap_uses_fresh_salt_and_nonce():
    vault_key = create_vault_key()
    first = wrap_master_key(vault_key, PASSWORD, "vault-001")
    second = wrap_master_key(vault_key, PASSWORD, "vault-001")

    assert first.kdf_salt != second.kdf_salt
    assert first.nonce != second.nonce
    assert first.ciphertext != second.ciphertext


def test_wrong_password_context_or_ciphertext_fails_generically():
    vault_key = create_vault_key()
    wrapper = wrap_master_key(vault_key, PASSWORD, "vault-001")

    with pytest.raises(InvalidMasterWrapper):
        unwrap_master_key(wrapper, "wrong password")
    with pytest.raises(InvalidMasterWrapper):
        unwrap_master_key(replace(wrapper, vault_id="different-vault"), PASSWORD)

    tampered = replace(wrapper, ciphertext=wrapper.ciphertext[:-1] + bytes([wrapper.ciphertext[-1] ^ 1]))
    with pytest.raises(InvalidMasterWrapper):
        unwrap_master_key(tampered, PASSWORD)


def test_master_wrapper_rejects_invalid_inputs():
    vault_key = create_vault_key()

    with pytest.raises(TypeError):
        wrap_master_key(vault_key.material, PASSWORD, "vault-001")
    with pytest.raises(ValueError):
        wrap_master_key(vault_key, PASSWORD, "")
