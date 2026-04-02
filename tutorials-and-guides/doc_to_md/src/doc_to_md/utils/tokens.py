"""Lightweight helpers around tiktoken for counting and chunking text."""
from __future__ import annotations

from functools import lru_cache
from typing import List

import tiktoken

DEFAULT_ENCODING = "cl100k_base"


@lru_cache
def _get_encoding(name: str = DEFAULT_ENCODING):
    return tiktoken.get_encoding(name)


def count_tokens(text: str, encoding_name: str = DEFAULT_ENCODING) -> int:
    """Return the number of tokens for ``text`` using the configured encoding."""
    if not text:
        return 0
    encoding = _get_encoding(encoding_name)
    return len(encoding.encode(text))


def split_by_tokens(
    text: str,
    max_tokens: int,
    overlap_tokens: int = 0,
    encoding_name: str = DEFAULT_ENCODING,
) -> List[str]:
    """Split ``text`` into overlapping segments using exact token counts."""
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    if overlap_tokens < 0:
        raise ValueError("overlap_tokens cannot be negative")
    if overlap_tokens >= max_tokens:
        raise ValueError("overlap_tokens must be smaller than max_tokens")

    encoding = _get_encoding(encoding_name)
    tokens = encoding.encode(text or "")
    if len(tokens) <= max_tokens:
        return [text]

    segments: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        segments.append(encoding.decode(chunk_tokens))
        if end == len(tokens):
            break
        start = end - overlap_tokens
    return segments
