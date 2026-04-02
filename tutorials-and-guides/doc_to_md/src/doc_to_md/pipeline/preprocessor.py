"""Preprocessing helpers before sending data to an engine."""
from __future__ import annotations

from pathlib import Path


def read_document(path: Path) -> bytes:
    """Return raw bytes for the downstream engine."""
    return path.read_bytes()
