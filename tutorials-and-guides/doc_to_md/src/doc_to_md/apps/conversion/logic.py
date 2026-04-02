"""Shared document conversion logic used by CLI and FastAPI."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import time
from typing import Dict, Optional, Type, cast

from doc_to_md.config.settings import EngineName, Settings, get_settings
from doc_to_md.engines.base import Engine
from doc_to_md.engines.auto import AutoEngine
from doc_to_md.engines.deepseekocr import DeepSeekOCREngine
from doc_to_md.engines.docling import DoclingEngine
from doc_to_md.engines.html import HtmlLocalEngine
from doc_to_md.engines.local import LocalEngine
from doc_to_md.engines.marker import MarkerEngine
from doc_to_md.engines.markitdown import MarkItDownEngine
from doc_to_md.engines.mineru import MinerUEngine
from doc_to_md.engines.mistral import MistralEngine
from doc_to_md.engines.opendataloader import OpenDataLoaderEngine
from doc_to_md.engines.paddleocr import PaddleOCREngine
from doc_to_md.pipeline.loader import iter_documents
from doc_to_md.pipeline.postprocessor import ConversionResult, enforce_markdown
from doc_to_md.pipeline.writer import write_markdown
from doc_to_md.utils.logging import log_error, log_info, log_warning
from doc_to_md.utils.validation import FileValidationError

ENGINE_REGISTRY: Dict[EngineName, Type[Engine]] = {
    "local": LocalEngine,
    "mistral": MistralEngine,
    "deepseekocr": DeepSeekOCREngine,
    "markitdown": MarkItDownEngine,
    "paddleocr": PaddleOCREngine,
    "mineru": MinerUEngine,
    "docling": DoclingEngine,
    "marker": MarkerEngine,
    "html_local": HtmlLocalEngine,
    "auto": AutoEngine,
    "opendataloader": OpenDataLoaderEngine,
}

ENGINES_REQUIRING_MODEL = {"deepseekocr", "mistral", "markitdown", "paddleocr", "mineru", "docling", "marker", "opendataloader"}


ENGINES_SUPPORTING_PAGE_OPTIONS = {"mistral"}


@dataclass(slots=True)
class RunMetrics:
    total_candidates: int = 0
    skipped_by_since: int = 0
    dry_run: int = 0
    successes: int = 0
    failures: int = 0

    @property
    def eligible(self) -> int:
        return self.total_candidates - self.skipped_by_since


@dataclass(slots=True)
class DocumentResult:
    source_path: Path
    status: str
    output_path: Path | None = None
    error: str | None = None
    modified_at: datetime | None = None


@dataclass(slots=True)
class ConversionRun:
    engine: str
    model: str | None
    input_dir: Path
    output_dir: Path
    metrics: RunMetrics
    duration_seconds: float
    results: list[DocumentResult] = field(default_factory=list)


def list_engine_names() -> list[str]:
    return list(ENGINE_REGISTRY)


def _resolve_engine(engine: EngineName, model: str | None, **engine_kwargs) -> Engine:
    if engine not in ENGINE_REGISTRY:
        raise ValueError(f"Unknown engine '{engine}'")
    engine_cls = ENGINE_REGISTRY[engine]
    # Only pass page-related kwargs to engines that support them
    if engine not in ENGINES_SUPPORTING_PAGE_OPTIONS:
        engine_kwargs.pop("include_page_headers", None)
    if engine in ENGINES_REQUIRING_MODEL:
        return engine_cls(model=model, **engine_kwargs)
    return engine_cls(**engine_kwargs)


def _normalize_engine(input_value: Optional[str], default: EngineName) -> EngineName:
    if input_value is None:
        return default
    candidate = input_value.lower()
    if candidate not in ENGINE_REGISTRY:
        raise ValueError(f"Unknown engine '{input_value}'")
    return cast(EngineName, candidate)


def _should_process(path: Path, since_timestamp: float | None) -> tuple[bool, float | None]:
    """Return whether a document should be processed and provide its mtime."""
    try:
        mtime = path.stat().st_mtime
    except FileNotFoundError:
        return False, None
    if since_timestamp is None:
        return True, mtime
    return mtime >= since_timestamp, mtime


def _format_summary(metrics: RunMetrics, elapsed_seconds: float) -> str:
    return (
        "Summary: "
        f"total={metrics.total_candidates}, "
        f"eligible={metrics.eligible}, "
        f"converted={metrics.successes}, "
        f"failed={metrics.failures}, "
        f"skipped_since={metrics.skipped_by_since}, "
        f"dry_run={metrics.dry_run}, "
        f"duration={elapsed_seconds:.2f}s"
    )


def run_conversion(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    engine: str | None = None,
    model: str | None = None,
    since: datetime | None = None,
    no_page_info: bool = False,
    dry_run: bool = False,
    settings: Settings | None = None,
) -> ConversionRun:
    active_settings = settings or get_settings()
    input_dir = Path(input_path) if input_path else active_settings.input_dir
    output_dir = Path(output_path) if output_path else active_settings.output_dir
    engine_name = _normalize_engine(engine, active_settings.default_engine)

    engine_kwargs: dict = {}
    if no_page_info:
        engine_kwargs["include_page_headers"] = False

    engine_instance = _resolve_engine(engine_name, model, **engine_kwargs)

    log_info(f"Using engine '{engine_name}' (model: {getattr(engine_instance, 'model', 'n/a')})")

    since_timestamp = since.timestamp() if since else None
    metrics = RunMetrics()
    results: list[DocumentResult] = []
    started_at = time.perf_counter()

    documents = list(iter_documents(input_dir))
    total_count = len(documents)
    if total_count == 0:
        log_warning(f"No documents found in {input_dir}")
        return ConversionRun(
            engine=engine_name,
            model=getattr(engine_instance, "model", model),
            input_dir=input_dir,
            output_dir=output_dir,
            metrics=metrics,
            duration_seconds=time.perf_counter() - started_at,
            results=results,
        )

    log_info(f"Found {total_count} document(s) to process")

    for index, source_path in enumerate(documents, start=1):
        metrics.total_candidates += 1
        should_process, mtime = _should_process(source_path, since_timestamp)
        modified_at = datetime.fromtimestamp(mtime) if mtime else None

        if not should_process:
            metrics.skipped_by_since += 1
            if since_timestamp is not None:
                stamp = modified_at.isoformat() if modified_at else "unknown"
                log_info(f"Skipping {source_path} (modified {stamp}) due to --since filter")
            results.append(DocumentResult(source_path=source_path, status="skipped", modified_at=modified_at))
            continue

        if dry_run:
            metrics.dry_run += 1
            log_info(f"[{index}/{total_count}] [dry-run] Would convert {source_path}")
            results.append(DocumentResult(source_path=source_path, status="dry_run", modified_at=modified_at))
            continue

        log_info(f"[{index}/{total_count}] Converting {source_path}")
        try:
            engine_response = engine_instance.convert(source_path)
        except FileValidationError as exc:
            log_error(f"Validation failed for {source_path.name}: {exc}")
            metrics.failures += 1
            results.append(DocumentResult(source_path=source_path, status="failed", error=str(exc), modified_at=modified_at))
            continue
        except Exception as exc:  # noqa: BLE001
            log_error(f"Failed to convert {source_path.name}: {exc}")
            metrics.failures += 1
            results.append(DocumentResult(source_path=source_path, status="failed", error=str(exc), modified_at=modified_at))
            continue

        result = ConversionResult(
            source_name=source_path.name,
            markdown=engine_response.markdown,
            engine=engine_instance.name,
            assets=engine_response.assets,
        )
        cleaned = enforce_markdown(result)
        target = write_markdown(cleaned, output_dir)
        log_info(f"[{index}/{total_count}] Wrote {target}")
        metrics.successes += 1
        results.append(DocumentResult(source_path=source_path, status="converted", output_path=target, modified_at=modified_at))

    elapsed = time.perf_counter() - started_at
    log_info(_format_summary(metrics, elapsed))
    return ConversionRun(
        engine=engine_name,
        model=getattr(engine_instance, "model", model),
        input_dir=input_dir,
        output_dir=output_dir,
        metrics=metrics,
        duration_seconds=elapsed,
        results=results,
    )
