"""Tests for vault-key creation and disclosure-safe representation."""

import pytest

from app.security.keys import VAULT_KEY_FORMAT_VERSION, VaultKey, create_vault_key
from app.security.randomness import VAULT_KEY_BYTES


def test_create_vault_key_returns_256_bit_material():
    key = create_vault_key()

    assert isinstance(key, VaultKey)
    assert len(key.material) == VAULT_KEY_BYTES == 32
    assert key.format_version == VAULT_KEY_FORMAT_VERSION


def test_each_vault_key_is_fresh():
    assert create_vault_key().material != create_vault_key().material


def test_vault_key_repr_does_not_include_key_material():
    material = b"A" * VAULT_KEY_BYTES
    key = VaultKey(material)

    assert material not in repr(key).encode("utf-8")


def test_vault_key_validates_material_and_version():
    with pytest.raises(TypeError):
        VaultKey("not bytes")
    with pytest.raises(ValueError):
        VaultKey(b"too short")
    with pytest.raises(ValueError):
        VaultKey(b"A" * VAULT_KEY_BYTES, format_version=2)
