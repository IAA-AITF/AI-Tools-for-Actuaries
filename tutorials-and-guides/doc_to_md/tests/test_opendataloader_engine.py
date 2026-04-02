"""Tests for the OpenDataLoader PDF engine."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from doc_to_md.engines.opendataloader import OpenDataLoaderEngine
from doc_to_md.engines.base import EngineResponse


# ---------------------------------------------------------------------------
# Engine metadata
# ---------------------------------------------------------------------------


def test_opendataloader_engine_name() -> None:
    engine = OpenDataLoaderEngine()
    assert engine.name == "opendataloader"


def test_opendataloader_default_model() -> None:
    engine = OpenDataLoaderEngine()
    assert engine.model == "opendataloader"


def test_opendataloader_custom_model() -> None:
    engine = OpenDataLoaderEngine(model="opendataloader-custom")
    assert engine.model == "opendataloader-custom"


# ---------------------------------------------------------------------------
# Settings are picked up
# ---------------------------------------------------------------------------


def test_opendataloader_hybrid_model_name() -> None:
    mock_settings = MagicMock()
    mock_settings.opendataloader_hybrid = "docling-fast"
    mock_settings.opendataloader_use_struct_tree = False

    with patch("doc_to_md.engines.opendataloader.get_settings", return_value=mock_settings):
        engine = OpenDataLoaderEngine()

    assert engine.model == "opendataloader-hybrid:docling-fast"
    assert engine._hybrid == "docling-fast"


def test_opendataloader_use_struct_tree_setting() -> None:
    mock_settings = MagicMock()
    mock_settings.opendataloader_hybrid = None
    mock_settings.opendataloader_use_struct_tree = True

    with patch("doc_to_md.engines.opendataloader.get_settings", return_value=mock_settings):
        engine = OpenDataLoaderEngine()

    assert engine._use_struct_tree is True


# ---------------------------------------------------------------------------
# Missing package raises helpful error
# ---------------------------------------------------------------------------


def test_opendataloader_missing_package_raises() -> None:
    engine = OpenDataLoaderEngine()
    import builtins
    real_import = builtins.__import__

    def _block_import(name, *args, **kwargs):
        if name == "opendataloader_pdf":
            raise ImportError("No module named 'opendataloader_pdf'")
        return real_import(name, *args, **kwargs)

    with patch.object(builtins, "__import__", side_effect=_block_import):
        with pytest.raises(RuntimeError, match="opendataloader-pdf"):
            engine._ensure_package()


# ---------------------------------------------------------------------------
# Java runtime checks
# ---------------------------------------------------------------------------


def test_ensure_java_not_on_path_raises() -> None:
    engine = OpenDataLoaderEngine()
    with patch("doc_to_md.engines.opendataloader.shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="java.*was not found on PATH"):
            engine._ensure_java()


def test_ensure_java_old_version_raises() -> None:
    engine = OpenDataLoaderEngine()
    # Simulate Java 8 (old versioning scheme: "1.8.0_321")
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stderr = 'java version "1.8.0_321"\n'
    mock_result.stdout = ""
    with patch("doc_to_md.engines.opendataloader.shutil.which", return_value="/usr/bin/java"), \
         patch("doc_to_md.engines.opendataloader.subprocess.run", return_value=mock_result):
        with pytest.raises(RuntimeError, match="Java 11\\+.*Java 8 was found"):
            engine._ensure_java()


def test_ensure_java_version_17_ok() -> None:
    engine = OpenDataLoaderEngine()
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stderr = 'openjdk version "17.0.1" 2021-10-19\n'
    mock_result.stdout = ""
    with patch("doc_to_md.engines.opendataloader.shutil.which", return_value="/usr/bin/java"), \
         patch("doc_to_md.engines.opendataloader.subprocess.run", return_value=mock_result):
        engine._ensure_java()  # should not raise


def test_ensure_java_version_11_ok() -> None:
    engine = OpenDataLoaderEngine()
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stderr = 'openjdk version "11.0.17" 2022-10-18\n'
    mock_result.stdout = ""
    with patch("doc_to_md.engines.opendataloader.shutil.which", return_value="/usr/bin/java"), \
         patch("doc_to_md.engines.opendataloader.subprocess.run", return_value=mock_result):
        engine._ensure_java()  # should not raise


def test_ensure_java_nonzero_exit_raises() -> None:
    engine = OpenDataLoaderEngine()
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "Error: Could not create the Java Virtual Machine."
    mock_result.stdout = ""
    with patch("doc_to_md.engines.opendataloader.shutil.which", return_value="/usr/bin/java"), \
         patch("doc_to_md.engines.opendataloader.subprocess.run", return_value=mock_result):
        with pytest.raises(RuntimeError, match="java -version.*failed with exit code 1"):
            engine._ensure_java()


def test_ensure_java_unparseable_version_raises() -> None:
    engine = OpenDataLoaderEngine()
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stderr = "some unexpected output with no version string"
    mock_result.stdout = ""
    with patch("doc_to_md.engines.opendataloader.shutil.which", return_value="/usr/bin/java"), \
         patch("doc_to_md.engines.opendataloader.subprocess.run", return_value=mock_result):
        with pytest.raises(RuntimeError, match="could not determine the Java version"):
            engine._ensure_java()


# ---------------------------------------------------------------------------
# Non-PDF input raises ValueError
# ---------------------------------------------------------------------------


def test_opendataloader_rejects_non_pdf(tmp_path: Path) -> None:
    txt_file = tmp_path / "document.txt"
    txt_file.write_text("hello", encoding="utf-8")

    engine = OpenDataLoaderEngine()
    # Patch both guards so we don't need the actual library or Java installed
    engine._ensure_java = lambda: None  # type: ignore[method-assign]
    engine._ensure_package = lambda: None  # type: ignore[method-assign]

    # Test the suffix guard by calling convert with a mocked package
    import sys
    fake_module = MagicMock()
    with patch.dict(sys.modules, {"opendataloader_pdf": fake_module}):
        with pytest.raises(ValueError, match="only supports PDF files"):
            engine.convert(txt_file)


# ---------------------------------------------------------------------------
# Successful conversion (mocked library call)
# ---------------------------------------------------------------------------


def test_opendataloader_convert_success(tmp_path: Path) -> None:
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake content")

    expected_markdown = "# Sample Document\n\nThis is the extracted text."

    def fake_convert(input_path, output_dir, format, **kwargs):
        # Simulate the library writing a markdown file to output_dir
        md_path = Path(output_dir) / "sample.md"
        md_path.write_text(expected_markdown, encoding="utf-8")

    import sys
    fake_module = MagicMock()
    fake_module.convert = fake_convert

    engine = OpenDataLoaderEngine()
    engine._ensure_java = lambda: None  # type: ignore[method-assign]
    with patch.dict(sys.modules, {"opendataloader_pdf": fake_module}):
        response = engine.convert(pdf_file)

    assert isinstance(response, EngineResponse)
    assert response.markdown == expected_markdown
    assert response.model == "opendataloader"
    assert response.assets == []


def test_opendataloader_convert_with_image_assets(tmp_path: Path) -> None:
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake content")

    md_text = "# Doc\n\nText with image."
    fake_image_bytes = b"\x89PNG\r\n"

    def fake_convert(input_path, output_dir, format, **kwargs):
        out = Path(output_dir)
        (out / "sample.md").write_text(md_text, encoding="utf-8")
        (out / "figure_1.png").write_bytes(fake_image_bytes)

    import sys
    fake_module = MagicMock()
    fake_module.convert = fake_convert

    engine = OpenDataLoaderEngine()
    engine._ensure_java = lambda: None  # type: ignore[method-assign]
    with patch.dict(sys.modules, {"opendataloader_pdf": fake_module}):
        response = engine.convert(pdf_file)

    assert response.markdown == md_text
    assert len(response.assets) == 1
    asset = response.assets[0]
    assert asset.filename == "figure_1.png"
    assert asset.data == fake_image_bytes
    assert asset.subdir == "images"


def test_opendataloader_convert_no_markdown_raises(tmp_path: Path) -> None:
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake content")

    def fake_convert(input_path, output_dir, format, **kwargs):
        # Simulate library producing no markdown output
        pass

    import sys
    fake_module = MagicMock()
    fake_module.convert = fake_convert

    engine = OpenDataLoaderEngine()
    engine._ensure_java = lambda: None  # type: ignore[method-assign]
    with patch.dict(sys.modules, {"opendataloader_pdf": fake_module}):
        with pytest.raises(RuntimeError, match="did not produce a Markdown file"):
            engine.convert(pdf_file)


def test_opendataloader_convert_multiple_markdown_raises(tmp_path: Path) -> None:
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake content")

    def fake_convert(input_path, output_dir, format, **kwargs):
        # Simulate library writing two unexpected .md files (not matching the input stem)
        out = Path(output_dir)
        (out / "partA.md").write_text("# Part A", encoding="utf-8")
        (out / "partB.md").write_text("# Part B", encoding="utf-8")

    import sys
    fake_module = MagicMock()
    fake_module.convert = fake_convert

    engine = OpenDataLoaderEngine()
    engine._ensure_java = lambda: None  # type: ignore[method-assign]
    with patch.dict(sys.modules, {"opendataloader_pdf": fake_module}):
        with pytest.raises(RuntimeError, match="multiple Markdown files"):
            engine.convert(pdf_file)


# ---------------------------------------------------------------------------
# Hybrid mode passes the right kwargs to the library
# ---------------------------------------------------------------------------


def test_opendataloader_hybrid_kwargs(tmp_path: Path) -> None:
    mock_settings = MagicMock()
    mock_settings.opendataloader_hybrid = "docling-fast"
    mock_settings.opendataloader_use_struct_tree = False

    pdf_file = tmp_path / "report.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 test")

    captured_kwargs: dict = {}

    def fake_convert(input_path, output_dir, format, **kwargs):
        captured_kwargs.update(kwargs)
        Path(output_dir, "report.md").write_text("# Hybrid result", encoding="utf-8")

    import sys
    fake_module = MagicMock()
    fake_module.convert = fake_convert

    with patch("doc_to_md.engines.opendataloader.get_settings", return_value=mock_settings):
        engine = OpenDataLoaderEngine()

    engine._ensure_java = lambda: None  # type: ignore[method-assign]
    with patch.dict(sys.modules, {"opendataloader_pdf": fake_module}):
        engine.convert(pdf_file)

    assert captured_kwargs.get("hybrid") == "docling-fast"
    assert "use_struct_tree" not in captured_kwargs


def test_opendataloader_struct_tree_kwargs(tmp_path: Path) -> None:
    mock_settings = MagicMock()
    mock_settings.opendataloader_hybrid = None
    mock_settings.opendataloader_use_struct_tree = True

    pdf_file = tmp_path / "tagged.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 test")

    captured_kwargs: dict = {}

    def fake_convert(input_path, output_dir, format, **kwargs):
        captured_kwargs.update(kwargs)
        Path(output_dir, "tagged.md").write_text("# Tagged PDF", encoding="utf-8")

    import sys
    fake_module = MagicMock()
    fake_module.convert = fake_convert

    with patch("doc_to_md.engines.opendataloader.get_settings", return_value=mock_settings):
        engine = OpenDataLoaderEngine()

    engine._ensure_java = lambda: None  # type: ignore[method-assign]
    with patch.dict(sys.modules, {"opendataloader_pdf": fake_module}):
        engine.convert(pdf_file)

    assert captured_kwargs.get("use_struct_tree") is True
    assert "hybrid" not in captured_kwargs


# ---------------------------------------------------------------------------
# Engine appears in global registry
# ---------------------------------------------------------------------------


def test_opendataloader_in_engine_registry() -> None:
    from doc_to_md.apps.conversion.logic import ENGINE_REGISTRY
    assert "opendataloader" in ENGINE_REGISTRY


def test_list_engine_names_includes_opendataloader() -> None:
    from doc_to_md.apps.conversion.logic import list_engine_names
    assert "opendataloader" in list_engine_names()


# ---------------------------------------------------------------------------
# Settings validation
# ---------------------------------------------------------------------------


def test_settings_opendataloader_defaults() -> None:
    from doc_to_md.config.settings import Settings
    s = Settings()
    assert s.opendataloader_hybrid is None
    assert s.opendataloader_use_struct_tree is False


def test_settings_opendataloader_hybrid_from_env(monkeypatch) -> None:
    monkeypatch.setenv("OPENDATALOADER_HYBRID", "docling-fast")
    from doc_to_md.config.settings import Settings
    s = Settings()
    assert s.opendataloader_hybrid == "docling-fast"


def test_settings_opendataloader_struct_tree_from_env(monkeypatch) -> None:
    monkeypatch.setenv("OPENDATALOADER_USE_STRUCT_TREE", "true")
    from doc_to_md.config.settings import Settings
    s = Settings()
    assert s.opendataloader_use_struct_tree is True
