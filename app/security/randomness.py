"""Cryptographically secure random material for the vault.

This module deliberately delegates randomness to Python's ``secrets`` module,
which uses the operating system's cryptographically secure random source. It
does not implement a custom pseudo-random generator or derive random material
from passwords, timestamps, identifiers, or other predictable values.
"""

import base64
import re
import secrets
import string


VAULT_KEY_BYTES = 32
# Legacy recovery keys were 32 decoded bytes encoded as Base32. New keys use
# a compact 16-character alphanumeric format while the decoder continues to
# accept the legacy format for already-created vaults.
RECOVERY_KEY_BYTES = 32
RECOVERY_KEY_LENGTH = 16
RECOVERY_KEY_ALPHABET = string.ascii_letters + string.digits
AES_GCM_NONCE_BYTES = 12
MAX_RANDOM_BYTES = 1024 * 1024
_BASE32_PATTERN = re.compile(r"[A-Z2-7]+")


def secure_random_bytes(length: int) -> bytes:
    """Return ``length`` bytes from the operating system CSPRNG."""

    if isinstance(length, bool) or not isinstance(length, int):
        raise TypeError("length must be an integer")
    if length <= 0 or length > MAX_RANDOM_BYTES:
        raise ValueError(f"length must be between 1 and {MAX_RANDOM_BYTES}")
    return secrets.token_bytes(length)


def generate_vault_key() -> bytes:
    """Generate the 256-bit key used later for vault-record encryption."""

    return secure_random_bytes(VAULT_KEY_BYTES)


def generate_aes_gcm_nonce() -> bytes:
    """Generate a fresh 96-bit AES-GCM nonce."""

    return secure_random_bytes(AES_GCM_NONCE_BYTES)


def generate_recovery_key() -> str:
    """Generate a fresh 16-character alphanumeric recovery key."""

    return "".join(secrets.choice(RECOVERY_KEY_ALPHABET) for _ in range(RECOVERY_KEY_LENGTH))


def decode_recovery_key(value: str) -> bytes:
    """Decode a formatted recovery key after canonicalizing separators.

    Invalid input raises ``ValueError``. The recovery workflow will translate
    this into a generic user-facing verification failure.
    """

    if not isinstance(value, str):
        raise TypeError("recovery key must be text")

    compact = re.sub(r"[-\s]", "", value)
    if len(compact) == RECOVERY_KEY_LENGTH and re.fullmatch(r"[A-Za-z0-9]{16}", compact):
        return compact.encode("ascii")

    legacy_compact = compact.upper()
    if not legacy_compact or not _BASE32_PATTERN.fullmatch(legacy_compact):
        raise ValueError("invalid recovery key format")

    padded = legacy_compact + "=" * (-len(legacy_compact) % 8)
    try:
        decoded = base64.b32decode(padded, casefold=False)
    except (base64.binascii.Error, ValueError) as exc:
        raise ValueError("invalid recovery key format") from exc

    if len(decoded) != RECOVERY_KEY_BYTES:
        raise ValueError("invalid recovery key length")
    return decoded
