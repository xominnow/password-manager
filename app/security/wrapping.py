"""Authenticated wrapping of the vault key with password or recovery KEKs."""

import json
from dataclasses import dataclass, field

from app.security.aead import (
    AES_GCM_TAG_BYTES,
    EncryptedPayload,
    InvalidCiphertext,
    decrypt_bytes,
    encrypt_bytes,
)
from app.security.kdf import (
    DEFAULT_SCRYPT_PARAMETERS,
    KDF_SALT_BYTES,
    ScryptParameters,
    derive_password_key,
    derive_recovery_key,
    generate_kdf_salt,
)
from app.security.keys import VaultKey
from app.security.randomness import (
    AES_GCM_NONCE_BYTES,
    VAULT_KEY_BYTES,
)


WRAPPER_FORMAT_VERSION = 1
MASTER_WRAPPER_PURPOSE = "master"
RECOVERY_WRAPPER_PURPOSE = "recovery"
class InvalidMasterWrapper(ValueError):
    """Generic failure raised when a master wrapper cannot be authenticated."""


def _wrapper_associated_data(vault_id: str, purpose: str) -> bytes:
    """Build deterministic non-secret context authenticated by AES-GCM."""

    return json.dumps(
        {
            "format_version": WRAPPER_FORMAT_VERSION,
            "purpose": purpose,
            "vault_id": vault_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _validate_wrapper_fields(
    *,
    vault_id: str,
    kdf_parameters: ScryptParameters,
    kdf_salt: bytes,
    nonce: bytes,
    ciphertext: bytes,
    format_version: int,
    purpose: str,
) -> None:
    if not isinstance(vault_id, str) or not vault_id:
        raise ValueError("vault_id must be non-empty text")
    if format_version != WRAPPER_FORMAT_VERSION:
        raise ValueError("unsupported wrapper format version")
    if not isinstance(kdf_parameters, ScryptParameters):
        raise TypeError("invalid KDF parameters")
    kdf_parameters.validate()
    if not isinstance(kdf_salt, bytes) or len(kdf_salt) != KDF_SALT_BYTES:
        raise ValueError("invalid KDF salt length")
    if not isinstance(nonce, bytes) or len(nonce) != AES_GCM_NONCE_BYTES:
        raise ValueError("invalid AES-GCM nonce length")
    if not isinstance(ciphertext, bytes) or len(ciphertext) < VAULT_KEY_BYTES + AES_GCM_TAG_BYTES:
        raise ValueError("invalid wrapped-key ciphertext")
    if purpose not in {MASTER_WRAPPER_PURPOSE, RECOVERY_WRAPPER_PURPOSE}:
        raise ValueError("invalid wrapper purpose")


def _unwrap_vault_key(kek: bytes, wrapper) -> VaultKey:
    try:
        plaintext = decrypt_bytes(
            kek,
            EncryptedPayload(nonce=wrapper.nonce, ciphertext=wrapper.ciphertext),
            wrapper.associated_data,
        )
        return VaultKey(plaintext)
    except (InvalidCiphertext, TypeError, ValueError) as exc:
        raise wrapper.invalid_error("wrapper authentication failed") from exc


@dataclass(frozen=True, slots=True)
class MasterKeyWrapper:
    """Persistable metadata and ciphertext for one master wrapper."""

    vault_id: str
    kdf_parameters: ScryptParameters
    kdf_salt: bytes = field(repr=False)
    nonce: bytes = field(repr=False)
    ciphertext: bytes = field(repr=False)
    format_version: int = WRAPPER_FORMAT_VERSION
    purpose: str = MASTER_WRAPPER_PURPOSE

    def __post_init__(self) -> None:
        if self.purpose != MASTER_WRAPPER_PURPOSE:
            raise ValueError("invalid master wrapper purpose")
        _validate_wrapper_fields(
            vault_id=self.vault_id,
            kdf_parameters=self.kdf_parameters,
            kdf_salt=self.kdf_salt,
            nonce=self.nonce,
            ciphertext=self.ciphertext,
            format_version=self.format_version,
            purpose=self.purpose,
        )

    @property
    def associated_data(self) -> bytes:
        """Return context reconstructed from authenticated wrapper metadata."""

        return _wrapper_associated_data(self.vault_id, self.purpose)

    invalid_error = InvalidMasterWrapper


def wrap_master_key(
    vault_key: VaultKey,
    password: str,
    vault_id: str,
    parameters: ScryptParameters = DEFAULT_SCRYPT_PARAMETERS,
) -> MasterKeyWrapper:
    """Wrap a vault key with a password-derived AES-256-GCM key."""

    if not isinstance(vault_key, VaultKey):
        raise TypeError("vault_key must be a VaultKey")

    kdf_salt = generate_kdf_salt()
    kek = derive_password_key(password, kdf_salt, parameters)
    encrypted = encrypt_bytes(
        kek,
        vault_key.material,
        _wrapper_associated_data(vault_id, MASTER_WRAPPER_PURPOSE),
    )
    return MasterKeyWrapper(
        vault_id=vault_id,
        kdf_parameters=parameters,
        kdf_salt=kdf_salt,
        nonce=encrypted.nonce,
        ciphertext=encrypted.ciphertext,
    )


def unwrap_master_key(wrapper: MasterKeyWrapper, password: str) -> VaultKey:
    """Authenticate and unwrap a vault key using the master password."""

    if not isinstance(wrapper, MasterKeyWrapper):
        raise TypeError("wrapper must be a MasterKeyWrapper")

    try:
        kek = derive_password_key(password, wrapper.kdf_salt, wrapper.kdf_parameters)
        return _unwrap_vault_key(kek, wrapper)
    except InvalidMasterWrapper:
        raise
    except (TypeError, ValueError) as exc:
        raise InvalidMasterWrapper("master wrapper authentication failed") from exc


class InvalidRecoveryWrapper(ValueError):
    """Generic failure raised when a recovery wrapper cannot be authenticated."""


@dataclass(frozen=True, slots=True)
class RecoveryKeyWrapper:
    """Persistable metadata and ciphertext for one recovery wrapper."""

    vault_id: str
    kdf_parameters: ScryptParameters
    kdf_salt: bytes = field(repr=False)
    nonce: bytes = field(repr=False)
    ciphertext: bytes = field(repr=False)
    format_version: int = WRAPPER_FORMAT_VERSION
    purpose: str = RECOVERY_WRAPPER_PURPOSE

    def __post_init__(self) -> None:
        if self.purpose != RECOVERY_WRAPPER_PURPOSE:
            raise ValueError("invalid recovery wrapper purpose")
        _validate_wrapper_fields(
            vault_id=self.vault_id,
            kdf_parameters=self.kdf_parameters,
            kdf_salt=self.kdf_salt,
            nonce=self.nonce,
            ciphertext=self.ciphertext,
            format_version=self.format_version,
            purpose=self.purpose,
        )

    @property
    def associated_data(self) -> bytes:
        """Return context reconstructed from authenticated wrapper metadata."""

        return _wrapper_associated_data(self.vault_id, self.purpose)

    invalid_error = InvalidRecoveryWrapper


def wrap_recovery_key(
    vault_key: VaultKey,
    recovery_key: bytes,
    vault_id: str,
    parameters: ScryptParameters = DEFAULT_SCRYPT_PARAMETERS,
) -> RecoveryKeyWrapper:
    """Wrap a vault key with a recovery-key-derived AES-256-GCM key."""

    if not isinstance(vault_key, VaultKey):
        raise TypeError("vault_key must be a VaultKey")

    kdf_salt = generate_kdf_salt()
    kek = derive_recovery_key(recovery_key, kdf_salt, parameters)
    encrypted = encrypt_bytes(
        kek,
        vault_key.material,
        _wrapper_associated_data(vault_id, RECOVERY_WRAPPER_PURPOSE),
    )
    return RecoveryKeyWrapper(
        vault_id=vault_id,
        kdf_parameters=parameters,
        kdf_salt=kdf_salt,
        nonce=encrypted.nonce,
        ciphertext=encrypted.ciphertext,
    )


def unwrap_recovery_key(wrapper: RecoveryKeyWrapper, recovery_key: bytes) -> VaultKey:
    """Authenticate and unwrap a vault key using canonical recovery bytes."""

    if not isinstance(wrapper, RecoveryKeyWrapper):
        raise TypeError("wrapper must be a RecoveryKeyWrapper")

    try:
        kek = derive_recovery_key(recovery_key, wrapper.kdf_salt, wrapper.kdf_parameters)
        return _unwrap_vault_key(kek, wrapper)
    except InvalidRecoveryWrapper:
        raise
    except (TypeError, ValueError) as exc:
        raise InvalidRecoveryWrapper("recovery wrapper authentication failed") from exc
