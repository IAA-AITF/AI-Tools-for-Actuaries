"""Engine adapter for the OpenDataLoader PDF parser."""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from doc_to_md.config.settings import get_settings

from .base import Engine, EngineAsset, EngineResponse


class OpenDataLoaderEngine(Engine):
    """Convert PDF files to Markdown using the opendataloader-pdf library.

    This engine wraps the ``opendataloader-pdf`` Python package, which uses a
    Java-based layout analysis pipeline and an optional AI hybrid backend for
    complex pages such as tables, scanned documents, and formulas.

    .. note::
        Java 11+ must be available on the system ``PATH``.
        Each :meth:`convert` call spawns a JVM subprocess, so it is slower for
        repeated single-file calls than bulk processing.
    """

    name = "opendataloader"

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self._hybrid: str | None = settings.opendataloader_hybrid
        self._use_struct_tree: bool = settings.opendataloader_use_struct_tree
        self.model = model or (f"opendataloader-hybrid:{self._hybrid}" if self._hybrid else "opendataloader")

    def _ensure_java(self) -> None:
        """Verify that a Java 11+ runtime is available on the system PATH."""
        if shutil.which("java") is None:
            raise RuntimeError(
                "OpenDataLoader engine requires Java 11+ but 'java' was not found on PATH. "
                "Install a JDK/JRE and ensure it is on your PATH, for example:\n"
                "  - Ubuntu/Debian: sudo apt install default-jre\n"
                "  - macOS (Homebrew): brew install openjdk@17\n"
                "  - Windows: https://adoptium.net/\n"
                "Then verify with: java -version"
            )
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "OpenDataLoader engine requires a working Java runtime, but "
                f"`java -version` failed with exit code {result.returncode}.\n"
                f"stdout: {result.stdout or '<empty>'}\n"
                f"stderr: {result.stderr or '<empty>'}"
            )
        version_output = result.stderr or result.stdout
        match = re.search(r'"(\d+)(?:\.(\d+))?', version_output)
        if not match:
            raise RuntimeError(
                "OpenDataLoader engine could not determine the Java version from "
                f"`java -version` output:\n{version_output}"
            )
        major = int(match.group(1))
        if major == 1:
            minor = int(match.group(2) or "0")
            effective = minor
        else:
            effective = major
        if effective < 11:
            raise RuntimeError(
                f"OpenDataLoader engine requires Java 11+, but Java {effective} was found. "
                "Please upgrade your Java installation."
            )

    def _ensure_package(self) -> None:
        try:
            import opendataloader_pdf  # noqa: F401
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "OpenDataLoader engine requires the `opendataloader-pdf` package. "
                "Install it via `pip install 'doc-to-markdown-converter[opendataloader]'` "
                "or `pip install opendataloader-pdf` and ensure Java 11+ is available."
            ) from exc

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - heavy dependency
        self._ensure_java()
        self._ensure_package()
        import opendataloader_pdf

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"OpenDataLoader engine only supports PDF files; got '{path.suffix}'.")

        with tempfile.TemporaryDirectory(prefix="opendataloader_") as temp_dir:
            convert_kwargs: dict = {
                # The library's API accepts a list of paths for batch processing.
                "input_path": [str(path)],
                "output_dir": temp_dir,
                "format": "markdown",
            }
            if self._hybrid:
                convert_kwargs["hybrid"] = self._hybrid
            if self._use_struct_tree:
                convert_kwargs["use_struct_tree"] = True

            opendataloader_pdf.convert(**convert_kwargs)

            # Prefer the expected <stem>.md output; fall back to sorted rglob
            # to avoid nondeterministic selection when multiple .md files exist.
            output_root = Path(temp_dir)
            expected_md = output_root / f"{path.stem}.md"
            if expected_md.is_file():
                md_path = expected_md
            else:
                md_files = sorted(output_root.rglob("*.md"))
                if not md_files:
                    raise RuntimeError("OpenDataLoader did not produce a Markdown file.")
                if len(md_files) > 1:
                    raise RuntimeError(
                        "OpenDataLoader produced multiple Markdown files; cannot determine "
                        f"which to use: {', '.join(str(p) for p in md_files)}"
                    )
                md_path = md_files[0]
            markdown = md_path.read_text(encoding="utf-8")

            assets: list[EngineAsset] = []
            for img_path in Path(temp_dir).rglob("*"):
                if img_path.is_file() and img_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
                    assets.append(
                        EngineAsset(
                            filename=img_path.name,
                            data=img_path.read_bytes(),
                            subdir="images",
                        )
                    )

        return EngineResponse(markdown=markdown, model=self.model, assets=assets)
