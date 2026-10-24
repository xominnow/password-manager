"""Vault setup and master-password authentication services."""

import string
from dataclasses import dataclass, field

from app.config import DEFAULT_SETTINGS
from app.security.keys import VaultKey, create_vault_key
from app.security.randomness import decode_recovery_key, generate_recovery_key, secure_random_bytes
from app.security.wrapping import (
    InvalidMasterWrapper,
    InvalidRecoveryWrapper,
    MasterKeyWrapper,
    RecoveryKeyWrapper,
    unwrap_master_key,
    unwrap_recovery_key,
    wrap_master_key,
    wrap_recovery_key,
)
from app.storage.sqlite import VaultDatabase


VAULT_ID_BYTES = 16


class VaultServiceError(ValueError):
    """Base error for setup and authentication failures."""


class VaultAlreadyInitialized(VaultServiceError):
    """Raised when setup is attempted for an existing local vault."""


class VaultNotInitialized(VaultServiceError):
    """Raised when login is attempted before setup."""


class AuthenticationError(VaultServiceError):
    """Generic master-password authentication failure."""


class RecoveryAuthenticationError(VaultServiceError):
    """Generic recovery-key authentication failure."""


class VaultCorruptError(VaultServiceError):
    """Raised when required vault metadata cannot be reconstructed safely."""


class PasswordPolicyError(VaultServiceError):
    """Raised when a master password fails the approved minimum policy."""


@dataclass(frozen=True, slots=True)
class VaultSetupResult:
    """Non-secret vault identity and the one-time recovery-key display value."""

    vault_id: bytes
    recovery_key: str = field(repr=False)


@dataclass(slots=True)
class UnlockedVaultSession:
    """In-memory unlocked session; the vault key is never persisted here."""

    vault_id: bytes
    _vault_key: VaultKey | None = field(default=None, repr=False)

    @property
    def vault_key(self) -> VaultKey:
        if self._vault_key is None:
            raise VaultServiceError("vault session is locked")
        return self._vault_key

    @property
    def is_unlocked(self) -> bool:
        return self._vault_key is not None

    def lock(self) -> None:
        self._vault_key = None


def validate_master_password(password: str) -> None:
    """Apply the approved minimum master-password policy."""

    if not isinstance(password, str):
        raise PasswordPolicyError("master password does not meet requirements")
    if len(password) < DEFAULT_SETTINGS.minimum_password_length:
        raise PasswordPolicyError("master password does not meet requirements")
    requirements = (
        DEFAULT_SETTINGS.require_uppercase and any(char.isupper() for char in password),
        DEFAULT_SETTINGS.require_lowercase and any(char.islower() for char in password),
        DEFAULT_SETTINGS.require_number and any(char.isdigit() for char in password),
        DEFAULT_SETTINGS.require_special_character and any(char in string.punctuation for char in password),
    )
    if not all(requirements):
        raise PasswordPolicyError("master password does not meet requirements")


class LocalVaultService:
    """Coordinates local vault setup and master-password login."""

    def __init__(self, database: VaultDatabase):
        self.database = database

    def setup(self, master_password: str) -> VaultSetupResult:
        validate_master_password(master_password)
        if self.database.get_vault_id() is not None:
            raise VaultAlreadyInitialized("vault is already initialized")

        vault_id = secure_random_bytes(VAULT_ID_BYTES)
        vault_context = vault_id.hex()
        vault_key = create_vault_key()
        recovery_key_text = self._new_recovery_key()
        recovery_key = decode_recovery_key(recovery_key_text)
        master_wrapper = wrap_master_key(vault_key, master_password, vault_context)
        recovery_wrapper = wrap_recovery_key(vault_key, recovery_key, vault_context)
        self.database.initialize_vault(vault_id, (master_wrapper, recovery_wrapper))
        return VaultSetupResult(vault_id=vault_id, recovery_key=recovery_key_text)

    @staticmethod
    def _new_recovery_key() -> str:
        return generate_recovery_key()

    def login(self, master_password: str) -> UnlockedVaultSession:
        vault_id = self.database.get_vault_id()
        if vault_id is None:
            raise VaultNotInitialized("vault is not initialized")

        row = self.database.get_wrapper("master")
        if row is None:
            raise VaultCorruptError("required master wrapper is missing")

        wrapper = self._master_wrapper_from_row(row, vault_id)
        try:
            vault_key = unwrap_master_key(wrapper, master_password)
        except (InvalidMasterWrapper, ValueError, TypeError) as exc:
            raise AuthenticationError("invalid master password") from exc
        return UnlockedVaultSession(vault_id=vault_id, _vault_key=vault_key)

    def reset_master_password(
        self,
        recovery_key_text: str,
        new_master_password: str,
    ) -> UnlockedVaultSession:
        """Replace the master wrapper after authenticating the recovery key."""

        validate_master_password(new_master_password)
        vault_id = self.database.get_vault_id()
        if vault_id is None:
            raise VaultNotInitialized("vault is not initialized")

        row = self.database.get_wrapper("recovery")
        if row is None:
            raise VaultCorruptError("required recovery wrapper is missing")

        wrapper = self._recovery_wrapper_from_row(row, vault_id)
        try:
            canonical_recovery_key = decode_recovery_key(recovery_key_text)
            vault_key = unwrap_recovery_key(wrapper, canonical_recovery_key)
        except (InvalidRecoveryWrapper, ValueError, TypeError) as exc:
            raise RecoveryAuthenticationError("invalid recovery key") from exc

        new_wrapper = wrap_master_key(vault_key, new_master_password, vault_id.hex())
        self.database.replace_master_wrapper(vault_id, new_wrapper)
        return UnlockedVaultSession(vault_id=vault_id, _vault_key=vault_key)

    @staticmethod
    def _master_wrapper_from_row(row, vault_id: bytes) -> MasterKeyWrapper:
        return LocalVaultService._wrapper_from_row(row, vault_id, MasterKeyWrapper)

    @staticmethod
    def _recovery_wrapper_from_row(row, vault_id: bytes) -> RecoveryKeyWrapper:
        return LocalVaultService._wrapper_from_row(row, vault_id, RecoveryKeyWrapper)

    @staticmethod
    def _wrapper_from_row(row, vault_id: bytes, wrapper_type):
        if row["encryption_algorithm"] != "aes-256-gcm":
            raise VaultCorruptError("unsupported wrapper encryption")
        if row["aad_version"] != row["format_version"]:
            raise VaultCorruptError("unsupported wrapper associated-data version")
        if bytes(row["vault_id"]) != vault_id:
            raise VaultCorruptError("wrapper belongs to a different vault")

        from app.security.kdf import ScryptParameters

        parameters = ScryptParameters(
            algorithm=row["kdf_algorithm"],
            n=row["kdf_n"],
            r=row["kdf_r"],
            p=row["kdf_p"],
            salt_length=len(row["kdf_salt"]),
            output_length=32,
        )
        return wrapper_type(
            vault_id=vault_id.hex(),
            kdf_parameters=parameters,
            kdf_salt=bytes(row["kdf_salt"]),
            nonce=bytes(row["nonce"]),
            ciphertext=bytes(row["wrapped_key"]),
            format_version=row["format_version"],
            purpose=row["purpose"],
        )
