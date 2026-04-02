"""Engine adapter for the Marker PDF project."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Dict

from doc_to_md.config.settings import get_settings
from doc_to_md.utils.hardware import ensure_marker_accelerator_env
from .base import Engine, EngineAsset, EngineResponse


class MarkerEngine(Engine):
    name = "marker"

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        ensure_marker_accelerator_env()
        self._cli_options: Dict[str, Any] = {
            "output_format": "markdown",
            "disable_image_extraction": not settings.marker_extract_images,
            "use_llm": settings.marker_use_llm,
        }
        if settings.marker_processors:
            self._cli_options["processors"] = settings.marker_processors
        if settings.marker_page_range:
            self._cli_options["page_range"] = settings.marker_page_range
        if settings.marker_llm_service:
            self._cli_options["llm_service"] = settings.marker_llm_service
            self._cli_options["use_llm"] = True
        self.model = model or settings.marker_llm_service or "marker"
        self._artifact_dict: Dict[str, Any] | None = None

    def _ensure_marker_runtime(self) -> tuple[Any, Any, Any]:
        try:
            from marker.config.parser import ConfigParser  # type: ignore
            from marker.models import create_model_dict  # type: ignore
            from marker.output import text_from_rendered  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Marker engine requires the `marker-pdf` package. "
                "Install it via `pip install marker-pdf` before using this engine."
            ) from exc
        return ConfigParser, create_model_dict, text_from_rendered

    def _ensure_artifacts(self, create_model_dict) -> Dict[str, Any]:
        if self._artifact_dict is None:
            self._artifact_dict = create_model_dict()
        return self._artifact_dict

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - heavy dependency
        ConfigParser, create_model_dict, text_from_rendered = self._ensure_marker_runtime()
        cli_options = dict(self._cli_options)
        config_parser = ConfigParser(cli_options)
        converter_cls = config_parser.get_converter_cls()
        converter = converter_cls(
            config=config_parser.generate_config_dict(),
            artifact_dict=self._ensure_artifacts(create_model_dict),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service(),
        )
        rendered = converter(str(path))
        markdown, _, images = text_from_rendered(rendered)

        assets: list[EngineAsset] = []
        for name, image in (images or {}).items():
            buffer = BytesIO()
            image.save(buffer, format=image.format or "PNG")
            assets.append(EngineAsset(filename=name, data=buffer.getvalue(), subdir="images"))

        return EngineResponse(markdown=markdown, model=self.model, assets=assets)
