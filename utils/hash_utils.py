"""Helpers for SHA-256 hashing and safe hash display."""

from __future__ import annotations

import hashlib
from typing import BinaryIO


def generate_file_hash(file_stream: BinaryIO, chunk_size: int = 4096) -> str:
    """Generate a SHA-256 hash for a file-like object using chunked reads."""
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    hasher = hashlib.sha256()
    start_position = None

    if hasattr(file_stream, "tell") and hasattr(file_stream, "seek"):
        start_position = file_stream.tell()
        file_stream.seek(0)

    try:
        while True:
            chunk = file_stream.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    finally:
        if start_position is not None:
            file_stream.seek(start_position)

    return hasher.hexdigest()


def shorten_hash(hash_value: str | None, visible_chars: int = 6) -> str:
    """Return a shortened hash for compact UI display."""
    if not hash_value:
        return "N/A"

    if len(hash_value) <= visible_chars * 2:
        return hash_value

    return f"{hash_value[:visible_chars]}...{hash_value[-visible_chars:]}"
