"""AES-256-GCM authenticated encryption for vault data."""

from dataclasses import dataclass, field

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.security.randomness import AES_GCM_NONCE_BYTES, generate_aes_gcm_nonce


AES_GCM_KEY_BYTES = 32
AES_GCM_TAG_BYTES = 16
AEAD_FORMAT_VERSION = 1


class InvalidCiphertext(ValueError):
    """Generic failure raised for invalid or unauthenticated ciphertext."""


@dataclass(frozen=True, slots=True)
class EncryptedPayload:
    """Nonce and authenticated ciphertext for one encryption operation."""

    nonce: bytes = field(repr=False)
    ciphertext: bytes = field(repr=False)
    format_version: int = AEAD_FORMAT_VERSION

    def __post_init__(self) -> None:
        if self.format_version != AEAD_FORMAT_VERSION:
            raise ValueError("unsupported encrypted-payload format version")
        if not isinstance(self.nonce, bytes) or len(self.nonce) != AES_GCM_NONCE_BYTES:
            raise ValueError("AES-GCM nonce must be 12 bytes")
        if not isinstance(self.ciphertext, bytes) or len(self.ciphertext) < AES_GCM_TAG_BYTES:
            raise ValueError("ciphertext must include a 16-byte authentication tag")


def _validate_key(key: bytes) -> None:
    if not isinstance(key, bytes) or len(key) != AES_GCM_KEY_BYTES:
        raise ValueError("AES-GCM key must be 32 bytes")


def _validate_associated_data(associated_data: bytes) -> None:
    if not isinstance(associated_data, bytes) or not associated_data:
        raise ValueError("associated data must be non-empty bytes")


def encrypt_bytes(key: bytes, plaintext: bytes, associated_data: bytes) -> EncryptedPayload:
    """Encrypt bytes with a fresh 96-bit nonce and authenticated context."""

    _validate_key(key)
    if not isinstance(plaintext, bytes):
        raise TypeError("plaintext must be bytes")
    _validate_associated_data(associated_data)

    nonce = generate_aes_gcm_nonce()
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, associated_data)
    return EncryptedPayload(nonce=nonce, ciphertext=ciphertext)


def decrypt_bytes(
    key: bytes,
    payload: EncryptedPayload,
    associated_data: bytes,
) -> bytes:
    """Authenticate and decrypt a payload without exposing partial plaintext."""

    _validate_key(key)
    if not isinstance(payload, EncryptedPayload):
        raise TypeError("payload must be an EncryptedPayload")
    _validate_associated_data(associated_data)

    try:
        return AESGCM(key).decrypt(payload.nonce, payload.ciphertext, associated_data)
    except InvalidTag as exc:
        raise InvalidCiphertext("ciphertext authentication failed") from exc
