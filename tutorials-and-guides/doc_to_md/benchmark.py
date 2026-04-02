#!/usr/bin/env python3
"""Benchmark document conversion engines on a single sample file."""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

settings_module = import_module("doc_to_md.config.settings")
logic_module = import_module("doc_to_md.apps.conversion.logic")
base_module = import_module("doc_to_md.engines.base")

EngineName = settings_module.EngineName
get_settings = settings_module.get_settings
ENGINE_REGISTRY = logic_module.ENGINE_REGISTRY
ENGINES_REQUIRING_MODEL = logic_module.ENGINES_REQUIRING_MODEL
Engine = base_module.Engine
EngineResponse = base_module.EngineResponse

ENGINE_NOTES: dict[str, dict[str, list[str] | str]] = {
    "paddleocr": {
        "label": "PaddleOCR",
        "pros": [
            "Can use a local GPU-backed OCR stack when Paddle is configured correctly.",
            "Works without an external OCR API.",
            "Useful when you want a pure OCR-oriented path instead of a full layout pipeline.",
        ],
        "cons": [
            "Runtime setup is heavier than the Python extra alone suggests.",
            "Windows GPU runs may require explicit CUDA DLL paths for the bundled Paddle runtime.",
            "This sample produced very little usable text despite a successful run.",
        ],
        "best_for": "Cases where you specifically want Paddle's OCR stack and are willing to manage the runtime.",
    },
    "docling": {
        "label": "Docling",
        "pros": [
            "Strong document structure recovery on complex PDFs.",
            "Good fit for enterprise reports and long-form documents.",
            "Runs locally once dependencies are installed.",
        ],
        "cons": [
            "Heavy dependency stack and slower startup.",
            "Runtime is usually much higher than API OCR on the same sample.",
            "Environment setup is less lightweight than core engines.",
        ],
        "best_for": "Complex PDFs where local structured extraction matters more than raw speed.",
    },
    "marker": {
        "label": "Marker",
        "pros": [
            "Produced the longest Markdown output in this benchmark.",
            "Recovered rich structure and extracted many page assets.",
            "Can be very strong when quality matters more than install simplicity.",
        ],
        "cons": [
            "Requires an isolated environment in this project because of dependency conflicts.",
            "Runtime on this sample was extremely high.",
            "Still shows OCR and punctuation artifacts in the output.",
        ],
        "best_for": "One-off or high-fidelity local conversions where heavy setup and long runtime are acceptable.",
    },
    "mineru": {
        "label": "MinerU",
        "pros": [
            "Recovered a usable long-form Markdown document after isolated-environment setup.",
            "Includes its own layout and OCR pipeline rather than relying on a remote API.",
            "Extracted a smaller, more restrained asset set than some other local engines.",
        ],
        "cons": [
            "Needed the most manual runtime repair to get working in this repository.",
            "Runtime was still very high on this sample.",
            "Output quality did not justify the setup cost compared with the better local alternatives.",
        ],
        "best_for": "Research or specialized evaluation work where you explicitly want to test MinerU despite its setup overhead.",
    },
    "opendataloader": {
        "label": "OpenDataLoader",
        "pros": [
            "Purpose-built PDF pipeline with Java-backed layout analysis.",
            "Supports hybrid mode for harder pages.",
            "Can be a strong local option once prerequisites are satisfied.",
        ],
        "cons": [
            "Requires both Java 11+ and the optional Python package.",
            "Current environment readiness is a hard prerequisite.",
            "PDF-only, so it is not a general document engine.",
        ],
        "best_for": "PDF-heavy workflows where you can maintain the Java runtime and optional package.",
    },
    "mistral": {
        "label": "Mistral OCR",
        "pros": [
            "Usually the easiest way to get high-quality OCR on difficult PDFs.",
            "No local OCR model installation required.",
            "Often the best speed-to-quality tradeoff when the API is available.",
        ],
        "cons": [
            "Requires a working API key and outbound network access.",
            "Usage is not free.",
            "Remote latency and service availability affect runtime.",
        ],
        "best_for": "Production OCR when quality and convenience matter more than avoiding API usage.",
    },
}


@dataclass
class EngineResult:
    """Result from testing a single engine."""

    engine_name: str
    model: str
    success: bool
    conversion_time: float
    markdown_length: int = 0
    num_assets: int = 0
    error_message: str | None = None
    markdown_path: str | None = None
    asset_dir: str | None = None


@dataclass
class BenchmarkResult:
    """Complete benchmark test results."""

    timestamp: str
    test_file: str
    file_size_bytes: int
    results: list[EngineResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "test_file": self.test_file,
            "file_size_bytes": self.file_size_bytes,
            "results": [asdict(result) for result in self.results],
        }


class EngineBenchmark:
    """Run benchmark comparisons across one or more engines."""

    def __init__(self, engines_to_test: list[tuple[EngineName, str | None]] | None = None):
        self.settings = get_settings()
        if engines_to_test is None:
            self.engines_to_test = [
                ("local", None),
                ("markitdown", None),
                ("paddleocr", None),
                ("docling", None),
                ("marker", None),
                ("mineru", None),
                ("mistral", self.settings.mistral_default_model),
                ("deepseekocr", self.settings.siliconflow_default_model),
                ("opendataloader", None),
            ]
        else:
            self.engines_to_test = engines_to_test

    def _create_engine(self, engine_name: EngineName, model: str | None) -> tuple[Engine | None, str | None]:
        try:
            engine_cls = ENGINE_REGISTRY.get(engine_name)
            if engine_cls is None:
                return None, f"Engine '{engine_name}' not found in registry."
            if engine_name in ENGINES_REQUIRING_MODEL:
                return engine_cls(model=model), None
            return engine_cls(), None
        except Exception as exc:  # noqa: BLE001
            return None, f"{type(exc).__name__}: {exc}"

    @staticmethod
    def _slugify(value: str) -> str:
        cleaned = [
            char.lower() if char.isalnum() else "_"
            for char in value
        ]
        slug = "".join(cleaned)
        while "__" in slug:
            slug = slug.replace("__", "_")
        return slug.strip("_") or "artifact"

    def _write_success_artifacts(
        self,
        *,
        engine_name: str,
        response: EngineResponse,
        output_dir: Path,
    ) -> tuple[str, str | None]:
        engine_dir = output_dir / "outputs" / self._slugify(engine_name)
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

    def _write_failure_artifact(self, *, engine_name: str, error_message: str, output_dir: Path) -> None:
        engine_dir = output_dir / "outputs" / self._slugify(engine_name)
        engine_dir.mkdir(parents=True, exist_ok=True)
        error_path = engine_dir / "error.txt"
        error_path.write_text(error_message, encoding="utf-8")

    def test_engine(
        self,
        engine_name: EngineName,
        model: str | None,
        test_file: Path,
        output_dir: Path,
    ) -> EngineResult:
        print(f"Testing engine: {engine_name} (model: {model or 'default'})")
        engine, create_error = self._create_engine(engine_name, model)
        if engine is None:
            error_message = create_error or "Failed to create engine instance."
            self._write_failure_artifact(engine_name=engine_name, error_message=error_message, output_dir=output_dir)
            print(f"  FAILED during initialization: {error_message}")
            return EngineResult(
                engine_name=engine_name,
                model=model or "default",
                success=False,
                conversion_time=0.0,
                error_message=error_message,
            )

        started_at = time.perf_counter()
        try:
            response: EngineResponse = engine.convert(test_file)
            conversion_time = time.perf_counter() - started_at
            markdown_path, asset_dir = self._write_success_artifacts(
                engine_name=engine_name,
                response=response,
                output_dir=output_dir,
            )
            result = EngineResult(
                engine_name=engine_name,
                model=response.model,
                success=True,
                conversion_time=conversion_time,
                markdown_length=len(response.markdown),
                num_assets=len(response.assets),
                markdown_path=markdown_path,
                asset_dir=asset_dir,
            )
            print(
                "  OK"
                f" | time={conversion_time:.2f}s"
                f" | markdown={result.markdown_length}"
                f" | assets={result.num_assets}"
            )
            return result
        except Exception as exc:  # noqa: BLE001
            conversion_time = time.perf_counter() - started_at
            error_message = f"{type(exc).__name__}: {exc}"
            self._write_failure_artifact(engine_name=engine_name, error_message=error_message, output_dir=output_dir)
            print(f"  FAILED after {conversion_time:.2f}s: {error_message}")
            return EngineResult(
                engine_name=engine_name,
                model=model or "default",
                success=False,
                conversion_time=conversion_time,
                error_message=error_message,
            )

    def run_benchmark(self, test_file: Path, output_dir: Path) -> BenchmarkResult:
        print("=" * 72)
        print("Starting benchmark")
        print(f"Test file: {test_file}")
        print(f"File size: {test_file.stat().st_size / 1024:.2f} KB")
        print("=" * 72)

        benchmark_result = BenchmarkResult(
            timestamp=datetime.now(timezone.utc).isoformat(),
            test_file=str(test_file),
            file_size_bytes=test_file.stat().st_size,
        )

        for engine_name, model in self.engines_to_test:
            benchmark_result.results.append(
                self.test_engine(
                    engine_name=engine_name,
                    model=model,
                    test_file=test_file,
                    output_dir=output_dir,
                )
            )

        return benchmark_result


class MarkdownReportGenerator:
    """Generate a readable Markdown report from benchmark results."""

    def __init__(self, benchmark_result: BenchmarkResult):
        self.result = benchmark_result

    @staticmethod
    def _format_duration(seconds: float) -> str:
        return f"{seconds:.2f}s"

    @staticmethod
    def _format_size(byte_count: int) -> str:
        if byte_count < 1024:
            return f"{byte_count} B"
        if byte_count < 1024 * 1024:
            return f"{byte_count / 1024:.2f} KB"
        return f"{byte_count / (1024 * 1024):.2f} MB"

    def _recommendation_lines(self) -> list[str]:
        lines: list[str] = []
        successful = [result for result in self.result.results if result.success]
        if not successful:
            lines.append("No engines completed successfully on this sample.")
            return lines

        fastest = min(successful, key=lambda result: result.conversion_time)
        richest = max(successful, key=lambda result: result.markdown_length)

        lines.append(
            f"- Fastest successful engine: `{fastest.engine_name}` at {self._format_duration(fastest.conversion_time)}."
        )
        lines.append(
            f"- Longest Markdown output: `{richest.engine_name}` with {richest.markdown_length:,} characters."
        )

        failed = [result for result in self.result.results if not result.success]
        if failed:
            blocked = ", ".join(f"`{result.engine_name}`" for result in failed)
            lines.append(f"- Engines blocked by setup or runtime issues on this machine: {blocked}.")

        return lines

    def generate_markdown_report(self) -> str:
        successful = [result for result in self.result.results if result.success]
        sorted_successes = sorted(successful, key=lambda result: result.conversion_time)

        lines: list[str] = []
        lines.append("# Benchmark Report")
        lines.append("")
        lines.append("## Sample")
        lines.append("")
        lines.append(f"- Timestamp: `{self.result.timestamp}`")
        lines.append(f"- Test file: `{self.result.test_file}`")
        lines.append(f"- File size: {self._format_size(self.result.file_size_bytes)}")
        lines.append(f"- Engines tested: {len(self.result.results)}")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.extend(self._recommendation_lines())
        lines.append("")

        if sorted_successes:
            lines.append("## Successful engines ranked by runtime")
            lines.append("")
            for rank, result in enumerate(sorted_successes, start=1):
                lines.append(
                    f"{rank}. `{result.engine_name}`"
                    f" - {self._format_duration(result.conversion_time)},"
                    f" {result.markdown_length:,} chars,"
                    f" {result.num_assets} assets"
                )
            lines.append("")

        lines.append("## Result table")
        lines.append("")
        lines.append("| Engine | Model | Status | Time | Markdown chars | Assets | Artifact |")
        lines.append("| --- | --- | --- | ---: | ---: | ---: | --- |")
        for result in self.result.results:
            artifact = result.markdown_path or "outputs/.../error.txt"
            status = "success" if result.success else "failed"
            markdown_length = f"{result.markdown_length:,}" if result.success else "-"
            asset_count = str(result.num_assets) if result.success else "-"
            duration = self._format_duration(result.conversion_time)
            lines.append(
                f"| `{result.engine_name}` | `{result.model}` | {status} | "
                f"{duration} | {markdown_length} | {asset_count} | `{artifact}` |"
            )
        lines.append("")

        failed = [result for result in self.result.results if not result.success]
        if failed:
            lines.append("## Failures")
            lines.append("")
            for result in failed:
                lines.append(f"### `{result.engine_name}`")
                lines.append("")
                lines.append("```text")
                lines.append(result.error_message or "Unknown error")
                lines.append("```")
                lines.append("")

        lines.append("## Engine notes")
        lines.append("")
        for result in self.result.results:
            notes = ENGINE_NOTES.get(result.engine_name)
            if notes is None:
                continue
            lines.append(f"### {notes['label']} (`{result.engine_name}`)")
            lines.append("")
            lines.append(f"- Best for: {notes['best_for']}")
            lines.append("- Pros:")
            for item in notes["pros"]:
                lines.append(f"  - {item}")
            lines.append("- Cons:")
            for item in notes["cons"]:
                lines.append(f"  - {item}")
            if result.success:
                lines.append(
                    f"- Measured on this sample: {self._format_duration(result.conversion_time)}, "
                    f"{result.markdown_length:,} Markdown chars, {result.num_assets} assets."
                )
            else:
                lines.append(f"- Measured on this sample: failed with `{result.error_message}`.")
            lines.append("")

        return "\n".join(lines)

    def save_report(self, output_dir: Path) -> Path:
        report_path = output_dir / "report.md"
        report_path.write_text(self.generate_markdown_report(), encoding="utf-8")
        return report_path


def resolve_engines(engine_names: list[str] | None) -> list[tuple[EngineName, str | None]] | None:
    if not engine_names:
        return None

    settings = get_settings()
    selected: list[tuple[EngineName, str | None]] = []
    for engine_name in engine_names:
        if engine_name == "mistral":
            selected.append((engine_name, settings.mistral_default_model))
        elif engine_name == "deepseekocr":
            selected.append((engine_name, settings.siliconflow_default_model))
        else:
            selected.append((engine_name, None))
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark document conversion engines.")
    parser.add_argument("--test-file", type=Path, required=True, help="Path to the input file to benchmark.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmark_results"),
        help="Directory where benchmark artifacts will be written.",
    )
    parser.add_argument(
        "--engines",
        type=str,
        nargs="+",
        help="List of engines to test, for example: docling opendataloader mistral",
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="Write `result.json` alongside the Markdown report.",
    )
    args = parser.parse_args()

    if not args.test_file.exists():
        raise SystemExit(f"Test file does not exist: {args.test_file}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    engines_to_test = resolve_engines(args.engines)

    benchmark = EngineBenchmark(engines_to_test)
    result = benchmark.run_benchmark(args.test_file, args.output_dir)

    report_path = MarkdownReportGenerator(result).save_report(args.output_dir)
    print("=" * 72)
    print(f"Report written to: {report_path}")

    if args.save_json:
        json_path = args.output_dir / "result.json"
        json_path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON written to: {json_path}")

    print("=" * 72)


if __name__ == "__main__":
    main()
