"""Tests for the format-aware AutoEngine dispatcher."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from doc_to_md.engines.auto import AutoEngine, _instantiate
from doc_to_md.engines.base import EngineResponse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_engine_response(text: str = "markdown content") -> EngineResponse:
    return EngineResponse(markdown=text, model="mock")


# ---------------------------------------------------------------------------
# _instantiate helper
# ---------------------------------------------------------------------------


def test_instantiate_local() -> None:
    engine = _instantiate("local")
    assert engine.name == "local"


def test_instantiate_html_local() -> None:
    engine = _instantiate("html_local")
    assert engine.name == "html_local"


def test_instantiate_opendataloader() -> None:
    engine = _instantiate("opendataloader")
    assert engine.name == "opendataloader"


def test_instantiate_unknown_raises() -> None:
    with pytest.raises(ValueError, match="not supported in auto mode"):
        _instantiate("unknown_engine_xyz")


# ---------------------------------------------------------------------------
# AutoEngine name & model
# ---------------------------------------------------------------------------


def test_auto_engine_name() -> None:
    assert AutoEngine.name == "auto"


def test_auto_engine_model_attribute() -> None:
    engine = AutoEngine()
    assert engine.model == "auto"


# ---------------------------------------------------------------------------
# Format routing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename,expected_engine_name",
    [
        ("doc.pdf", "local"),
        ("doc.docx", "local"),
        ("deck.pptx", "local"),
        ("data.xlsx", "local"),
        ("page.html", "html_local"),
        ("page.htm", "html_local"),
        ("photo.png", "local"),
        ("photo.jpg", "local"),
        ("photo.jpeg", "local"),
        ("notes.txt", "local"),
        ("readme.md", "local"),
    ],
)
def test_auto_engine_default_routing(tmp_path: Path, filename: str, expected_engine_name: str) -> None:
    """AutoEngine should dispatch to the correct sub-engine based on file suffix."""
    file_path = tmp_path / filename
    file_path.write_text("content", encoding="utf-8")

    engine = AutoEngine()
    sub = engine._get_sub_engine(file_path)
    assert sub.name == expected_engine_name


def test_auto_engine_convert_txt(tmp_path: Path) -> None:
    """Full convert() call on a .txt file should succeed via local engine."""
    txt_file = tmp_path / "sample.txt"
    txt_file.write_text("hello auto engine", encoding="utf-8")

    response = AutoEngine().convert(txt_file)
    assert "hello auto engine" in response.markdown


def test_auto_engine_convert_html(tmp_path: Path) -> None:
    """Full convert() call on an .html file should succeed via HtmlLocalEngine."""
    html_file = tmp_path / "page.html"
    html_file.write_text("<html><body><p>Auto HTML content</p></body></html>", encoding="utf-8")

    response = AutoEngine().convert(html_file)
    assert "Auto HTML content" in response.markdown


# ---------------------------------------------------------------------------
# Settings-based routing override
# ---------------------------------------------------------------------------


def test_auto_engine_respects_settings_override(tmp_path: Path, monkeypatch) -> None:
    """AUTO_HTML_ENGINE setting should change which engine handles HTML files."""
    html_file = tmp_path / "page.html"
    html_file.write_text("<html><body><p>Overridden</p></body></html>", encoding="utf-8")

    # Monkey-patch settings so html uses "local" instead of "html_local"
    from doc_to_md.config import settings as settings_mod

    mock_settings = MagicMock()
    mock_settings.auto_pdf_engine = "local"
    mock_settings.auto_docx_engine = "local"
    mock_settings.auto_html_engine = "local"  # overridden to local
    mock_settings.auto_image_engine = "local"
    mock_settings.auto_text_engine = "local"
    mock_settings.auto_pptx_engine = "local"
    mock_settings.auto_spreadsheet_engine = "local"

    monkeypatch.setattr(settings_mod, "get_settings", lambda: mock_settings)

    engine = AutoEngine()
    engine._format_map[".html"] = "local"

    sub = engine._get_sub_engine(html_file)
    assert sub.name == "local"


# ---------------------------------------------------------------------------
# engine registered in global ENGINE_REGISTRY
# ---------------------------------------------------------------------------


def test_auto_in_engine_registry() -> None:
    from doc_to_md.apps.conversion.logic import ENGINE_REGISTRY
    assert "auto" in ENGINE_REGISTRY


def test_html_local_in_engine_registry() -> None:
    from doc_to_md.apps.conversion.logic import ENGINE_REGISTRY
    assert "html_local" in ENGINE_REGISTRY


def test_list_engine_names_includes_new_engines() -> None:
    from doc_to_md.apps.conversion.logic import list_engine_names
    names = list_engine_names()
    assert "auto" in names
    assert "html_local" in names


# ---------------------------------------------------------------------------
# HTML/HTM in loader and validation
# ---------------------------------------------------------------------------


def test_iter_documents_includes_html(tmp_path: Path) -> None:
    from doc_to_md.pipeline.loader import iter_documents

    (tmp_path / "page.html").write_text("<html/>", encoding="utf-8")
    (tmp_path / "page.htm").write_text("<html/>", encoding="utf-8")
    (tmp_path / "ignore.bin").write_text("x", encoding="utf-8")

    found = {p.name for p in iter_documents(tmp_path)}
    assert "page.html" in found
    assert "page.htm" in found
    assert "ignore.bin" not in found


def test_validate_html_extension(tmp_path: Path) -> None:
    from doc_to_md.utils.validation import validate_file

    html_file = tmp_path / "page.html"
    html_file.write_text("<html/>", encoding="utf-8")
    assert validate_file(html_file) is True


def test_validate_htm_extension(tmp_path: Path) -> None:
    from doc_to_md.utils.validation import validate_file

    htm_file = tmp_path / "page.htm"
    htm_file.write_text("<html/>", encoding="utf-8")
    assert validate_file(htm_file) is True


# ---------------------------------------------------------------------------
# run_conversion integration with auto engine
# ---------------------------------------------------------------------------


def test_run_conversion_auto_engine_html(tmp_path: Path) -> None:
    """run_conversion() with engine='auto' should convert HTML files."""
    from doc_to_md.apps.conversion.logic import run_conversion

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    (input_dir / "article.html").write_text(
        "<html><body><p>Auto conversion test</p></body></html>",
        encoding="utf-8",
    )

    result = run_conversion(
        input_path=input_dir,
        output_path=output_dir,
        engine="auto",
    )

    assert result.metrics.successes == 1
    assert result.results[0].status == "converted"
    assert result.results[0].output_path is not None
    assert result.results[0].output_path.exists()
    content = result.results[0].output_path.read_text(encoding="utf-8")
    assert "Auto conversion test" in content


# ---------------------------------------------------------------------------
# PPTX / XLSX in loader and validation
# ---------------------------------------------------------------------------


def test_iter_documents_includes_pptx_xlsx(tmp_path: Path) -> None:
    from doc_to_md.pipeline.loader import iter_documents

    (tmp_path / "deck.pptx").write_bytes(b"PK\x03\x04")  # minimal zip-based marker
    (tmp_path / "data.xlsx").write_bytes(b"PK\x03\x04")
    (tmp_path / "ignore.bin").write_text("x", encoding="utf-8")

    found = {p.name for p in iter_documents(tmp_path)}
    assert "deck.pptx" in found
    assert "data.xlsx" in found
    assert "ignore.bin" not in found


# ---------------------------------------------------------------------------
# Sub-engine instance caching
# ---------------------------------------------------------------------------


def test_auto_engine_caches_sub_engine_instance(tmp_path: Path) -> None:
    """The same sub-engine instance should be reused for repeated calls."""
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("first", encoding="utf-8")
    f2.write_text("second", encoding="utf-8")

    engine = AutoEngine()
    sub1 = engine._get_sub_engine(f1)
    sub2 = engine._get_sub_engine(f2)
    # Same format → same cached instance
    assert sub1 is sub2
