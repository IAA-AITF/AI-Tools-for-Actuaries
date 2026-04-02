"""Engine adapter for MinerU's document parsing pipeline."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Callable, Tuple

from doc_to_md.config.settings import get_settings
from doc_to_md.utils.hardware import ensure_mineru_accelerator_env
from .base import Engine, EngineAsset, EngineResponse


class MinerUEngine(Engine):
    name = "mineru"

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self.backend = settings.mineru_backend
        self.parse_method = settings.mineru_parse_method
        self.lang = settings.mineru_lang
        self.formula_enable = settings.mineru_formula_enable
        self.table_enable = settings.mineru_table_enable
        self.start_page = settings.mineru_start_page
        self.end_page = settings.mineru_end_page
        # Model metadata is descriptive only; MinerU is a local pipeline.
        self.model = model or f"{self.backend}:{self.parse_method}"
        self._runtime: Tuple[
            Callable[..., Any], Callable[..., bytes], Any
        ] | None = None  # (do_parse, read_fn, MakeMode)
        ensure_mineru_accelerator_env()

    def _ensure_runtime(self) -> Tuple[Callable[..., Any], Callable[..., bytes], Any]:
        if self._runtime is not None:
            return self._runtime
        try:
            from mineru.cli.common import do_parse, read_fn  # type: ignore
            from mineru.utils.enum_class import MakeMode  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "MinerU engine requires the `mineru` package and its dependencies. "
                "Install it via `pip install mineru` before using this engine."
            ) from exc

        self._runtime = (do_parse, read_fn, MakeMode)
        return self._runtime

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - heavy dependency
        do_parse, read_fn, MakeMode = self._ensure_runtime()
        pdf_bytes = read_fn(path)
        with tempfile.TemporaryDirectory(prefix="mineru_") as temp_dir:
            do_parse(
                output_dir=temp_dir,
                pdf_file_names=[path.stem],
                pdf_bytes_list=[pdf_bytes],
                p_lang_list=[self.lang],
                backend=self.backend,
                parse_method=self.parse_method,
                formula_enable=self.formula_enable,
                table_enable=self.table_enable,
                start_page_id=self.start_page,
                end_page_id=self.end_page,
                # Keep disk spill minimal; we only care about Markdown and images.
                f_draw_layout_bbox=False,
                f_draw_span_bbox=False,
                f_dump_md=True,
                f_dump_middle_json=False,
                f_dump_model_output=False,
                f_dump_orig_pdf=False,
                f_dump_content_list=False,
                f_make_md_mode=MakeMode.MM_MD,
            )

            parse_folder = self._resolve_output_folder(Path(temp_dir), path.stem)
            markdown_path = parse_folder / f"{path.stem}.md"
            if not markdown_path.exists():
                raise RuntimeError("MinerU did not produce a Markdown file.")
            markdown = markdown_path.read_text(encoding="utf-8")

            assets: list[EngineAsset] = []
            images_dir = parse_folder / "images"
            if images_dir.exists():
                for file_path in images_dir.glob("*"):
                    if file_path.is_file():
                        assets.append(
                            EngineAsset(
                                filename=file_path.name,
                                data=file_path.read_bytes(),
                                subdir="images",
                            )
                        )

        return EngineResponse(markdown=markdown, model=self.model, assets=assets)

    def _resolve_output_folder(self, root: Path, stem: str) -> Path:
        if self.backend == "pipeline":
            subfolder = self.parse_method
        else:
            subfolder = "vlm"
        parse_folder = root / stem / subfolder
        if not parse_folder.exists():
            raise RuntimeError(f"MinerU output folder {parse_folder} is missing.")
        return parse_folder
