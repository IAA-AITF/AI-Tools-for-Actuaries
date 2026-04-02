"""Abstractions for pluggable conversion engines."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol, TypeVar


@dataclass(slots=True)
class EngineAsset:
    """Binary artifact generated alongside Markdown output (e.g., images)."""

    filename: str
    data: bytes
    subdir: str | None = None


@dataclass(slots=True)
class EngineResponse:
    markdown: str
    model: str
    assets: list[EngineAsset] = field(default_factory=list)


class Engine(Protocol):
    name: str

    def convert(self, path: Path) -> EngineResponse:
        ...


T = TypeVar("T")


class RetryableRequestMixin:
    """Shared retry/backoff handling for engines that make network calls."""

    retry_attempts: int
    _retry_backoff: float

    def __init__(self, retry_attempts: int, retry_backoff: float = 1.5) -> None:
        self.retry_attempts = retry_attempts
        self._retry_backoff = retry_backoff

    def _request_with_retry(self, func: Callable[[], T], operation: str) -> T:
        delay = self._retry_backoff
        last_exc: Exception | None = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                return func()
            except Exception as exc:  # noqa: BLE001 - bubble after retries
                last_exc = exc
                if attempt == self.retry_attempts:
                    break
                time.sleep(delay)
                delay *= 2
        assert last_exc is not None
        raise RuntimeError(f"Operation '{operation}' failed after {self.retry_attempts} attempts") from last_exc
