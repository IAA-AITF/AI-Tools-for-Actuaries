"""Engine adapter for IBM's Docling converter."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from doc_to_md.config.settings import get_settings
from doc_to_md.utils.hardware import ensure_docling_accelerator_env
from .base import Engine, EngineResponse


class DoclingEngine(Engine):
    name = "docling"

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self.model = model or "docling"
        self._max_pages = settings.docling_max_pages
        self._raises_on_error = settings.docling_raise_on_error
        self._converter: Any | None = None

    def _ensure_converter(self) -> Any:
        if self._converter is not None:
            return self._converter
        try:
            from docling.document_converter import DocumentConverter
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Docling engine requires the `docling` package. "
                "Install it with `pip install docling` (or an equivalent extra) before using this engine."
            ) from exc

        # HF Hub tries to create symlinks when caching models. On Windows without developer
        # privileges this fails, so force the hub to fall back to copy semantics instead.
        try:  # pragma: no cover - environment specific
            from huggingface_hub import file_download as hf_file_download
        except Exception:  # noqa: BLE001 - best effort
            pass
        else:
            hf_file_download.are_symlinks_supported = lambda cache_dir=None: False  # type: ignore[assignment]

        ensure_docling_accelerator_env()
        self._converter = DocumentConverter()
        return self._converter

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - heavy dependency
        converter = self._ensure_converter()
        kwargs: dict[str, Any] = {"raises_on_error": self._raises_on_error}
        if self._max_pages is not None:
            kwargs["max_num_pages"] = self._max_pages
        result = converter.convert(str(path), **kwargs)
        document = getattr(result, "document", None)
        if document is None:
            raise RuntimeError("Docling did not return a document object.")
        markdown = document.export_to_markdown()
        return EngineResponse(markdown=markdown, model=self.model)
