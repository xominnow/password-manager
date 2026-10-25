"""Encrypted credential creation service."""

import json
import uuid
from dataclasses import dataclass, field, replace

from app.security.aead import InvalidCiphertext, decrypt_bytes, encrypt_bytes
from app.security.vault_service import UnlockedVaultSession
from app.storage.sqlite import DatabaseError, VaultDatabase


RECORD_VERSION = 1
RECORD_TYPE = "credential"


class CredentialValidationError(ValueError):
    """Raised when a credential cannot be safely created."""


class CredentialReadError(ValueError):
    """Generic failure raised when an encrypted credential cannot be read."""


class CredentialNotFoundError(ValueError):
    """Raised when an edit targets an entry that is not in the selected vault."""


MASKED_PASSWORD = "••••••••"


@dataclass(frozen=True, slots=True)
class CredentialRecord:
    """Transient credential result returned after an encrypted insert."""

    entry_id: str
    app_name: str
    username: str
    password: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class CredentialView:
    """Display-safe credential view with password hidden by default."""

    entry_id: str
    app_name: str
    username: str
    _password: str = field(repr=False)
    password_visible: bool = False

    @property
    def displayed_password(self) -> str:
        return self._password if self.password_visible else MASKED_PASSWORD

    def reveal(self) -> "CredentialView":
        """Return a view explicitly authorized to display the password."""

        return replace(self, password_visible=True)

    def hide(self) -> "CredentialView":
        """Return a masked view."""

        return replace(self, password_visible=False)


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CredentialValidationError(f"{field_name} is required")
    return value.strip()


def serialize_credential(app_name: str, username: str, password: str) -> bytes:
    """Serialize a credential canonically for transient encryption only."""

    app_name = _required_text(app_name, "app_name")
    username = _required_text(username, "username")
    if not isinstance(password, str) or not password:
        raise CredentialValidationError("password is required")
    return json.dumps(
        {
            "app_name": app_name,
            "password": password,
            "username": username,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def entry_associated_data(vault_id: bytes, entry_id: str) -> bytes:
    """Build deterministic context binding a record to its vault and identity."""

    if not isinstance(vault_id, bytes) or not vault_id:
        raise CredentialValidationError("vault_id is required")
    if not isinstance(entry_id, str) or not entry_id:
        raise CredentialValidationError("entry_id is required")
    return json.dumps(
        {
            "format_version": RECORD_VERSION,
            "record_id": entry_id,
            "record_type": RECORD_TYPE,
            "vault_id": vault_id.hex(),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _deserialize_credential(payload: bytes, entry_id: str) -> CredentialView:
    try:
        data = json.loads(payload.decode("utf-8"))
        if set(data) != {"app_name", "password", "username"}:
            raise ValueError("unexpected credential fields")
        app_name = _required_text(data["app_name"], "app_name")
        username = _required_text(data["username"], "username")
        password = data["password"]
        if not isinstance(password, str) or not password:
            raise ValueError("invalid password field")
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CredentialReadError("credential could not be read") from exc
    return CredentialView(entry_id, app_name, username, password)


class CredentialService:
    """Manages encrypted credential records for an authenticated session."""

    def __init__(self, database: VaultDatabase):
        self.database = database

    def create(
        self,
        session: UnlockedVaultSession,
        app_name: str,
        username: str,
        password: str,
    ) -> CredentialRecord:
        """Encrypt and atomically insert one credential record."""

        if not isinstance(session, UnlockedVaultSession) or not session.is_unlocked:
            raise CredentialValidationError("vault must be unlocked")

        app_name = _required_text(app_name, "app_name")
        username = _required_text(username, "username")
        if not isinstance(password, str) or not password:
            raise CredentialValidationError("password is required")

        entry_id = uuid.uuid4().hex
        plaintext = serialize_credential(app_name, username, password)
        associated_data = entry_associated_data(session.vault_id, entry_id)
        encrypted_payload = encrypt_bytes(session.vault_key.material, plaintext, associated_data)
        self.database.insert_entry(entry_id, session.vault_id, encrypted_payload)
        return CredentialRecord(entry_id, app_name, username, password)

    def view(
        self,
        session: UnlockedVaultSession,
        entry_id: str,
    ) -> CredentialView | None:
        """Decrypt one record and return a password-masked view."""

        if not isinstance(session, UnlockedVaultSession) or not session.is_unlocked:
            raise CredentialValidationError("vault must be unlocked")
        if not isinstance(entry_id, str) or not entry_id:
            raise CredentialValidationError("entry_id is required")

        encrypted_payload = self.database.get_entry(entry_id)
        if encrypted_payload is None:
            return None
        try:
            plaintext = decrypt_bytes(
                session.vault_key.material,
                encrypted_payload,
                entry_associated_data(session.vault_id, entry_id),
            )
        except (InvalidCiphertext, TypeError, ValueError) as exc:
            raise CredentialReadError("credential could not be read") from exc
        return _deserialize_credential(plaintext, entry_id)

    def search(
        self,
        session: UnlockedVaultSession,
        query: str = "",
    ) -> tuple[CredentialView, ...]:
        """Search app/website names after authenticated in-memory decryption.

        Because app names are part of the encrypted payload, SQLite cannot
        search them directly. An empty query returns all entries; otherwise,
        matching is a case-insensitive substring search over app names.
        Passwords remain masked in every returned view.
        """

        if not isinstance(session, UnlockedVaultSession) or not session.is_unlocked:
            raise CredentialValidationError("vault must be unlocked")
        if not isinstance(query, str):
            raise CredentialValidationError("search query must be text")
        normalized_query = query.strip().casefold()

        results: list[CredentialView] = []
        for entry_id, encrypted_payload in self.database.list_entries(session.vault_id):
            try:
                plaintext = decrypt_bytes(
                    session.vault_key.material,
                    encrypted_payload,
                    entry_associated_data(session.vault_id, entry_id),
                )
            except (InvalidCiphertext, TypeError, ValueError) as exc:
                raise CredentialReadError("credential could not be read") from exc
            view = _deserialize_credential(plaintext, entry_id)
            if normalized_query in view.app_name.casefold():
                results.append(view)

        return tuple(sorted(results, key=lambda item: (item.app_name.casefold(), item.entry_id)))

    def update(
        self,
        session: UnlockedVaultSession,
        entry_id: str,
        app_name: str,
        username: str,
        password: str,
    ) -> CredentialRecord:
        """Encrypt and atomically replace one credential record.

        The entry identifier and authenticated-data context remain stable while
        ``encrypt_bytes`` creates a fresh nonce for the replacement payload.
        SQLite receives only the encrypted payload and never the field values.
        """

        if not isinstance(session, UnlockedVaultSession) or not session.is_unlocked:
            raise CredentialValidationError("vault must be unlocked")
        if not isinstance(entry_id, str) or not entry_id:
            raise CredentialValidationError("entry_id is required")

        app_name = _required_text(app_name, "app_name")
        username = _required_text(username, "username")
        if not isinstance(password, str) or not password:
            raise CredentialValidationError("password is required")

        plaintext = serialize_credential(app_name, username, password)
        encrypted_payload = encrypt_bytes(
            session.vault_key.material,
            plaintext,
            entry_associated_data(session.vault_id, entry_id),
        )
        try:
            self.database.update_entry(
                entry_id,
                session.vault_id,
                encrypted_payload,
            )
        except DatabaseError as exc:
            raise CredentialNotFoundError("credential entry does not exist") from exc
        return CredentialRecord(entry_id, app_name, username, password)

    def delete(
        self,
        session: UnlockedVaultSession,
        entry_id: str,
        *,
        confirmed: bool = False,
    ) -> bool:
        """Delete one entry only after the caller explicitly confirms.

        The database operation is scoped to the authenticated session's vault
        and is transaction-backed. A missing entry returns ``False`` so the UI
        can show a generic unavailable result without exposing other vaults.
        """

        if not isinstance(session, UnlockedVaultSession) or not session.is_unlocked:
            raise CredentialValidationError("vault must be unlocked")
        if not isinstance(entry_id, str) or not entry_id:
            raise CredentialValidationError("entry_id is required")
        if confirmed is not True:
            raise CredentialValidationError("delete confirmation is required")
        return self.database.delete_entry(entry_id, session.vault_id)
