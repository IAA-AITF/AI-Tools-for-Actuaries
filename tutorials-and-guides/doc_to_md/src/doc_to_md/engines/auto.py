"""Format-aware engine that dispatches to the best sub-engine for each file type."""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Mapping

from .base import Engine, EngineResponse

_AUTO_REGISTRY: Mapping[str, tuple[str, str, bool]] = {
    "local": ("doc_to_md.engines.local", "LocalEngine", False),
    "html_local": ("doc_to_md.engines.html", "HtmlLocalEngine", False),
    "markitdown": ("doc_to_md.engines.markitdown", "MarkItDownEngine", True),
    "mistral": ("doc_to_md.engines.mistral", "MistralEngine", True),
    "deepseekocr": ("doc_to_md.engines.deepseekocr", "DeepSeekOCREngine", True),
    "paddleocr": ("doc_to_md.engines.paddleocr", "PaddleOCREngine", True),
    "docling": ("doc_to_md.engines.docling", "DoclingEngine", True),
    "marker": ("doc_to_md.engines.marker", "MarkerEngine", True),
    "mineru": ("doc_to_md.engines.mineru", "MinerUEngine", True),
    "opendataloader": ("doc_to_md.engines.opendataloader", "OpenDataLoaderEngine", False),
}

# Keys must stay in sync with SUPPORTED_EXTENSIONS in utils/validation.py.
_DEFAULT_FORMAT_ENGINES: Mapping[str, str] = {
    ".pdf": "local",
    ".docx": "local",
    ".pptx": "local",
    ".xlsx": "local",
    ".html": "html_local",
    ".htm": "html_local",
    ".png": "local",
    ".jpg": "local",
    ".jpeg": "local",
    ".txt": "local",
    ".md": "local",
}


def _instantiate(engine_name: str, model: str | None = None) -> Engine:
    """Create an engine instance by name using lazy imports to avoid circular deps."""
    entry = _AUTO_REGISTRY.get(engine_name)
    if entry is None:
        raise ValueError(
            f"Engine '{engine_name}' is not supported in auto mode. "
            f"Supported engines: {sorted(_AUTO_REGISTRY)}"
        )
    module_path, class_name, requires_model = entry
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(model=model) if requires_model else cls()


class AutoEngine(Engine):
    """Format-aware dispatcher that selects the best sub-engine per file type.

    The sub-engine used for each format is configured via ``Settings``:

    * ``AUTO_PDF_ENGINE``          - engine for .pdf files   (default: ``local``)
    * ``AUTO_DOCX_ENGINE``         - engine for .docx files  (default: ``local``)
    * ``AUTO_PPTX_ENGINE``         - engine for .pptx files  (default: ``local``)
    * ``AUTO_SPREADSHEET_ENGINE``  - engine for .xlsx files  (default: ``local``)
    * ``AUTO_HTML_ENGINE``         - engine for .html/.htm   (default: ``html_local``)
    * ``AUTO_IMAGE_ENGINE``        - engine for image files  (default: ``local``)
    * ``AUTO_TEXT_ENGINE``         - engine for .txt/.md     (default: ``local``)

    Any engine supported by the main ``ENGINE_REGISTRY`` can be used as a
    format sub-engine as long as it is listed in ``_AUTO_REGISTRY`` above.

    Sub-engine instances are cached per engine name so that engines which
    perform model or library initialization are only set up once per conversion
    run, not once per file.
    """

    name = "auto"

    def __init__(self) -> None:
        from doc_to_md.config.settings import get_settings

        settings = get_settings()
        self.model = "auto"
        self._format_map: dict[str, str] = {
            ".pdf": settings.auto_pdf_engine,
            ".docx": settings.auto_docx_engine,
            ".pptx": settings.auto_pptx_engine,
            ".xlsx": settings.auto_spreadsheet_engine,
            ".html": settings.auto_html_engine,
            ".htm": settings.auto_html_engine,
            ".png": settings.auto_image_engine,
            ".jpg": settings.auto_image_engine,
            ".jpeg": settings.auto_image_engine,
            ".txt": settings.auto_text_engine,
            ".md": settings.auto_text_engine,
        }
        self._engine_cache: dict[str, Engine] = {}

    def _get_sub_engine(self, path: Path) -> Engine:
        suffix = path.suffix.lower()
        engine_name = self._format_map.get(suffix, _DEFAULT_FORMAT_ENGINES.get(suffix, "local"))
        if engine_name not in self._engine_cache:
            self._engine_cache[engine_name] = _instantiate(engine_name)
        return self._engine_cache[engine_name]

    def convert(self, path: Path) -> EngineResponse:
        sub_engine = self._get_sub_engine(path)
        return sub_engine.convert(path)
