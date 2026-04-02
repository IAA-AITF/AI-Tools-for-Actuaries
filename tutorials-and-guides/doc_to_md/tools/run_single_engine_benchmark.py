#!/usr/bin/env python3
"""Run one engine against one file without importing the full engine registry."""
from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

ENGINE_SPECS: dict[str, tuple[str, str]] = {
    "docling": ("doc_to_md.engines.docling", "DoclingEngine"),
    "local": ("doc_to_md.engines.local", "LocalEngine"),
    "marker": ("doc_to_md.engines.marker", "MarkerEngine"),
    "markitdown": ("doc_to_md.engines.markitdown", "MarkItDownEngine"),
    "mineru": ("doc_to_md.engines.mineru", "MinerUEngine"),
    "opendataloader": ("doc_to_md.engines.opendataloader", "OpenDataLoaderEngine"),
    "paddleocr": ("doc_to_md.engines.paddleocr", "PaddleOCREngine"),
}


@dataclass
class EngineResult:
    engine_name: str
    model: str
    success: bool
    conversion_time: float
    markdown_length: int = 0
    num_assets: int = 0
    error_message: str | None = None
    markdown_path: str | None = None
    asset_dir: str | None = None


def slugify(value: str) -> str:
    cleaned = [char.lower() if char.isalnum() else "_" for char in value]
    slug = "".join(cleaned)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "artifact"


def load_engine(engine_name: str, model: str | None):
    if engine_name not in ENGINE_SPECS:
        raise SystemExit(f"Unsupported engine '{engine_name}'.")
    module_name, class_name = ENGINE_SPECS[engine_name]
    module = importlib.import_module(module_name)
    engine_cls = getattr(module, class_name)
    if model is None:
        return engine_cls()
    return engine_cls(model=model)


def write_success_artifacts(*, engine_name: str, response, output_dir: Path) -> tuple[str, str | None]:
    engine_dir = output_dir / "outputs" / slugify(engine_name)
    if engine_dir.exists():
        shutil.rmtree(engine_dir)
    engine_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = engine_dir / "output.md"
    markdown_path.write_text(response.markdown, encoding="utf-8")

    asset_root = engine_dir / "assets"
    asset_dir_path: Path | None = None
    if response.assets:
        asset_dir_path = asset_root
        for asset in response.assets:
            subdir = asset.subdir or ""
            target_dir = asset_root / subdir
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / asset.filename
            target_path.write_bytes(asset.data)

    return str(markdown_path.relative_to(output_dir)), (
        str(asset_dir_path.relative_to(output_dir)) if asset_dir_path else None
    )


def write_failure_artifact(*, engine_name: str, error_message: str, output_dir: Path) -> None:
    engine_dir = output_dir / "outputs" / slugify(engine_name)
    if engine_dir.exists():
        shutil.rmtree(engine_dir)
    engine_dir.mkdir(parents=True, exist_ok=True)
    (engine_dir / "error.txt").write_text(error_message, encoding="utf-8")


def run_once(*, engine_name: str, model: str | None, test_file: Path, output_dir: Path) -> EngineResult:
    engine = load_engine(engine_name, model)
    started = time.perf_counter()
    try:
        response = engine.convert(test_file)
        elapsed = time.perf_counter() - started
        markdown_path, asset_dir = write_success_artifacts(
            engine_name=engine_name,
            response=response,
            output_dir=output_dir,
        )
        return EngineResult(
            engine_name=engine_name,
            model=response.model,
            success=True,
            conversion_time=elapsed,
            markdown_length=len(response.markdown),
            num_assets=len(response.assets),
            markdown_path=markdown_path,
            asset_dir=asset_dir,
        )
    except Exception as exc:  # noqa: BLE001
        elapsed = time.perf_counter() - started
        error_message = f"{type(exc).__name__}: {exc}"
        write_failure_artifact(engine_name=engine_name, error_message=error_message, output_dir=output_dir)
        return EngineResult(
            engine_name=engine_name,
            model=model or engine_name,
            success=False,
            conversion_time=elapsed,
            error_message=error_message,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one engine against one file.")
    parser.add_argument("--engine", required=True)
    parser.add_argument("--test-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--result-path", type=Path, default=None)
    args = parser.parse_args()

    if not args.test_file.exists():
        raise SystemExit(f"Test file does not exist: {args.test_file}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = run_once(
        engine_name=args.engine,
        model=args.model,
        test_file=args.test_file,
        output_dir=args.output_dir,
    )
    payload = json.dumps(asdict(result), ensure_ascii=False, indent=2)
    if args.result_path is not None:
        args.result_path.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
