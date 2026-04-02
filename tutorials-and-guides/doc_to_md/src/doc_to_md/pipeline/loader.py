"""Utilities for loading documents from disk."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from doc_to_md.utils.validation import SUPPORTED_EXTENSIONS


def iter_documents(input_dir: Path) -> Iterable[Path]:
    """Yield supported documents under ``input_dir`` recursively."""
    for path in input_dir.rglob("*"):
        if path.suffix.lower() in SUPPORTED_EXTENSIONS and path.is_file():
            yield path
