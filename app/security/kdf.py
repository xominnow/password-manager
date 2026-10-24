"""Scrypt key derivation for password and recovery-key protection."""

from dataclasses import dataclass

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from app.security.randomness import RECOVERY_KEY_BYTES, secure_random_bytes


KDF_SALT_BYTES = 16
KDF_OUTPUT_BYTES = 32
MIN_SCRYPT_N = 2**16
MIN_SCRYPT_R = 8
MIN_SCRYPT_P = 1


@dataclass(frozen=True, slots=True)
class ScryptParameters:
    """Versioned Scrypt parameters with an approved memory-cost floor."""

    algorithm: str = "scrypt"
    n: int = MIN_SCRYPT_N
    r: int = MIN_SCRYPT_R
    p: int = MIN_SCRYPT_P
    salt_length: int = KDF_SALT_BYTES
    output_length: int = KDF_OUTPUT_BYTES

    def validate(self) -> None:
        """Reject unsupported algorithms and parameters below the security floor."""

        if self.algorithm != "scrypt":
            raise ValueError("only Scrypt is supported")
        if self.n < MIN_SCRYPT_N or self.n <= 1 or self.n & (self.n - 1):
            raise ValueError("Scrypt n must be a power of two at the approved floor")
        if self.r < MIN_SCRYPT_R:
            raise ValueError("Scrypt r is below the approved security floor")
        if self.p < MIN_SCRYPT_P:
            raise ValueError("Scrypt p must be positive")
        if self.salt_length != KDF_SALT_BYTES:
            raise ValueError("salt length must be 16 bytes")
        if self.output_length != KDF_OUTPUT_BYTES:
            raise ValueError("output length must be 32 bytes")


DEFAULT_SCRYPT_PARAMETERS = ScryptParameters()


def generate_kdf_salt() -> bytes:
    """Generate a fresh independent salt for one derivation."""

    return secure_random_bytes(KDF_SALT_BYTES)


def _secret_bytes(secret: str | bytes) -> bytes:
    if isinstance(secret, str):
        encoded = secret.encode("utf-8")
    elif isinstance(secret, bytes):
        encoded = secret
    else:
        raise TypeError("secret must be text or bytes")

    if not encoded:
        raise ValueError("secret must not be empty")
    return encoded


def derive_key(
    secret: str | bytes,
    salt: bytes,
    parameters: ScryptParameters = DEFAULT_SCRYPT_PARAMETERS,
) -> bytes:
    """Derive a raw key-encryption key with Scrypt."""

    parameters.validate()
    if not isinstance(salt, bytes):
        raise TypeError("salt must be bytes")
    if len(salt) != parameters.salt_length:
        raise ValueError("salt has an invalid length")

    return Scrypt(
        salt=salt,
        length=parameters.output_length,
        n=parameters.n,
        r=parameters.r,
        p=parameters.p,
    ).derive(_secret_bytes(secret))


def derive_password_key(
    password: str,
    salt: bytes,
    parameters: ScryptParameters = DEFAULT_SCRYPT_PARAMETERS,
) -> bytes:
    """Derive a key-encryption key from a user-entered master password."""

    return derive_key(password, salt, parameters)


def derive_recovery_key(
    recovery_key: bytes,
    salt: bytes,
    parameters: ScryptParameters = DEFAULT_SCRYPT_PARAMETERS,
) -> bytes:
    """Derive a key-encryption key from canonical recovery-key bytes."""

    if len(recovery_key) not in {16, RECOVERY_KEY_BYTES}:
        raise ValueError("recovery key must be 16 or 32 bytes")
    return derive_key(recovery_key, salt, parameters)
