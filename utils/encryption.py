"""Optional AES-backed encryption helpers for stored hashes."""

from __future__ import annotations

import os
from functools import lru_cache

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover - handled at runtime when package is absent
    Fernet = None
    InvalidToken = Exception


TRUTHY_VALUES = {"1", "true", "yes", "on"}


def _encryption_requested() -> bool:
    return os.getenv("ENABLE_HASH_ENCRYPTION", "false").strip().lower() in TRUTHY_VALUES


def encryption_enabled() -> bool:
    return _encryption_requested() and Fernet is not None


def validate_encryption_configuration() -> None:
    """Validate encryption settings during app startup."""
    if not _encryption_requested():
        return

    if Fernet is None:
        raise RuntimeError(
            "Hash encryption is enabled, but the 'cryptography' package is not installed."
        )

    if not os.getenv("HASH_ENCRYPTION_KEY"):
        raise RuntimeError(
            "HASH_ENCRYPTION_KEY must be set when ENABLE_HASH_ENCRYPTION is true."
        )

    _get_cipher()


@lru_cache(maxsize=1)
def _get_cipher():
    if not encryption_enabled():
        return None

    key = os.getenv("HASH_ENCRYPTION_KEY", "").encode("utf-8")
    return Fernet(key)


def encrypt_hash_value(hash_value: str) -> str:
    """Encrypt the supplied hash when encryption is enabled."""
    cipher = _get_cipher()
    if cipher is None:
        return hash_value
    return cipher.encrypt(hash_value.encode("utf-8")).decode("utf-8")


def decrypt_hash_value(stored_value: str) -> str:
    """Decrypt the stored hash value when encryption is enabled."""
    if not stored_value:
        return ""

    cipher = _get_cipher()
    if cipher is None:
        return stored_value

    try:
        return cipher.decrypt(stored_value.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return stored_value
