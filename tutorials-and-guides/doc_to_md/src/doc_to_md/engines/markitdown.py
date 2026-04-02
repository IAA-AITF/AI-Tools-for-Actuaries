"""Engine that relies on Microsoft's MarkItDown library for rich conversions."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from doc_to_md.config.settings import get_settings
from .base import Engine, EngineResponse


class MarkItDownEngine(Engine):
    name = "markitdown"

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self.model = model or "markitdown"
        self._converter = self._build_converter(
            enable_plugins=settings.markitdown_enable_plugins,
            enable_builtins=settings.markitdown_enable_builtins,
        )

    @staticmethod
    def _build_converter(**options: Any) -> Any:
        try:
            from markitdown import MarkItDown
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "MarkItDown engine requires the `markitdown` package. "
                "Install it via `pip install markitdown` before using this engine."
            ) from exc

        sanitized: Dict[str, Any] = {k: v for k, v in options.items() if v is not None}
        return MarkItDown(**sanitized)

    def convert(self, path: Path) -> EngineResponse:
        result = self._converter.convert(str(path))
        markdown = getattr(result, "markdown", None) or getattr(result, "text_content", "")
        if not markdown.strip():
            markdown = "_MarkItDown returned an empty response._"
        return EngineResponse(markdown=markdown, model=self.model)
