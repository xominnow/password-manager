"""Typed key material used by the vault security core."""

from dataclasses import dataclass, field

from app.security.randomness import VAULT_KEY_BYTES, generate_vault_key


VAULT_KEY_FORMAT_VERSION = 1


@dataclass(frozen=True, slots=True)
class VaultKey:
    """An in-memory 256-bit vault-encryption key.

    The key bytes are excluded from the default representation to reduce the
    chance of accidental disclosure through logs, tracebacks, or debugging.
    Persistence and key wrapping are implemented by later security tasks.
    """

    _material: bytes = field(repr=False)
    format_version: int = VAULT_KEY_FORMAT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self._material, bytes):
            raise TypeError("vault key material must be bytes")
        if len(self._material) != VAULT_KEY_BYTES:
            raise ValueError("vault key material must be 32 bytes")
        if self.format_version != VAULT_KEY_FORMAT_VERSION:
            raise ValueError("unsupported vault key format version")

    @property
    def material(self) -> bytes:
        """Return the immutable key bytes for an approved crypto operation."""

        return self._material


def create_vault_key() -> VaultKey:
    """Generate a fresh random vault-encryption key."""

    return VaultKey(generate_vault_key())
