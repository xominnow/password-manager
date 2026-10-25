"""Disk/log secrecy and legacy recovery compatibility verification."""

import base64
import secrets

from app.security.vault_service import LocalVaultService
from app.services.credentials import CredentialService
from app.storage.sqlite import VaultDatabase


def test_secrets_absent_from_disk_and_captured_logs(tmp_path, caplog, capsys):
    master = "Audit Master!729"
    password = "AuditCredential!938"
    username = "audit-only-user-938@example.invalid"
    path = tmp_path / "audit.sqlite3"
    with VaultDatabase(path) as database:
        service = LocalVaultService(database)
        setup = service.setup(master)
        session = service.login(master)
        credentials = CredentialService(database)
        record = credentials.create(session, "Audit-only app 938", username, password)
        assert credentials.view(session, record.entry_id).reveal().displayed_password == password
        session.lock()

    captured = capsys.readouterr()
    for secret in (master, setup.recovery_key, username, password, "Audit-only app 938"):
        assert secret not in caplog.text + captured.out + captured.err
        for file in tmp_path.iterdir():
            if file.is_file():
                assert secret.encode("utf-8") not in file.read_bytes()


def test_legacy_recovery_key_still_recovers_existing_entries(monkeypatch):
    legacy = base64.b32encode(secrets.token_bytes(32)).decode("ascii").rstrip("=")
    grouped = "-".join(legacy[i:i + 4] for i in range(0, len(legacy), 4))
    monkeypatch.setattr(LocalVaultService, "_new_recovery_key", staticmethod(lambda: grouped))
    with VaultDatabase(":memory:") as database:
        service = LocalVaultService(database)
        service.setup("Legacy Master!729")
        old_session = service.login("Legacy Master!729")
        credentials = CredentialService(database)
        record = credentials.create(old_session, "Legacy app", "dummy", "LegacyCredential!938")
        old_session.lock()
        recovered = service.reset_master_password(grouped.lower(), "Replacement Master!729")
        assert credentials.view(recovered, record.entry_id).reveal().displayed_password == "LegacyCredential!938"
