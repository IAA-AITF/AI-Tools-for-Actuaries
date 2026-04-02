"""Local fallback engine that attempts lightweight text extraction."""
from __future__ import annotations

from pathlib import Path

from .base import Engine, EngineResponse
from doc_to_md.pipeline.text_extraction import extract_text


class LocalEngine(Engine):
    name = "local"

    def convert(self, path: Path) -> EngineResponse:
        text = extract_text(path)
        if not text.strip():
            text = "_No textual content could be extracted._"

        markdown = f"# {path.stem}\n\n{text}\n"
        return EngineResponse(markdown=markdown, model="local-text-wrapper")
