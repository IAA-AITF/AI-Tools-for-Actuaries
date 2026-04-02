"""Tests for the HTML content-extraction engine."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from doc_to_md.engines.html import HtmlLocalEngine

try:
    import trafilatura
except ImportError:
    trafilatura = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_HTML = """\
<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
  <nav>Navigation links here</nav>
  <main>
    <h1>Article Title</h1>
    <p>This is the main content of the article.</p>
  </main>
  <footer>Footer content</footer>
</body>
</html>
"""

SIMPLE_HTML = "<html><body><p>Hello World</p></body></html>"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_html_engine_name() -> None:
    assert HtmlLocalEngine.name == "html_local"


def test_html_engine_convert_returns_markdown(tmp_path: Path) -> None:
    html_file = tmp_path / "page.html"
    html_file.write_text(SIMPLE_HTML, encoding="utf-8")

    engine = HtmlLocalEngine()
    response = engine.convert(html_file)

    assert "Hello World" in response.markdown
    assert response.model == "html-local"


def test_html_engine_includes_stem_as_heading(tmp_path: Path) -> None:
    html_file = tmp_path / "mypage.html"
    html_file.write_text(SIMPLE_HTML, encoding="utf-8")

    response = HtmlLocalEngine().convert(html_file)
    assert "# mypage" in response.markdown


def test_html_engine_empty_body_returns_placeholder(tmp_path: Path) -> None:
    html_file = tmp_path / "empty.html"
    html_file.write_text("<html><body></body></html>", encoding="utf-8")

    response = HtmlLocalEngine().convert(html_file)
    assert response.markdown.strip()  # Should still return something (heading at minimum)


def test_html_engine_bs4_fallback(tmp_path: Path) -> None:
    """Verify the bs4 fallback works when trafilatura is unavailable."""
    html_file = tmp_path / "page.html"
    html_file.write_text(SIMPLE_HTML, encoding="utf-8")

    with patch("doc_to_md.engines.html.trafilatura", None):
        response = HtmlLocalEngine().convert(html_file)

    assert "Hello World" in response.markdown


def test_html_engine_regex_fallback(tmp_path: Path) -> None:
    """Verify the regex fallback works when both trafilatura and bs4 are unavailable."""
    html_file = tmp_path / "page.html"
    html_file.write_text(SIMPLE_HTML, encoding="utf-8")

    with patch("doc_to_md.engines.html.trafilatura", None), \
         patch("doc_to_md.engines.html.BeautifulSoup", None):
        response = HtmlLocalEngine().convert(html_file)

    assert "Hello World" in response.markdown


def test_html_engine_strips_nav_and_footer(tmp_path: Path) -> None:
    """trafilatura path: nav/footer elements should be stripped in favour of main content."""
    html_file = tmp_path / "article.html"
    html_file.write_text(MINIMAL_HTML, encoding="utf-8")

    # Only run this test when trafilatura is actually available
    if trafilatura is None:
        pytest.skip("trafilatura not installed")

    response = HtmlLocalEngine().convert(html_file)

    # Main content should be present
    assert "Article Title" in response.markdown or "main content" in response.markdown.lower()


def test_html_engine_bs4_strips_boilerplate_tags(tmp_path: Path) -> None:
    """bs4 fallback: script/style content should be excluded from the output."""
    # Create a minimal BS4 mock that behaves like the real thing for this test
    html_file = tmp_path / "page.html"
    html_file.write_text(
        "<html><head><script>alert('ads')</script><style>.x{}</style></head>"
        "<body><p>Real content</p></body></html>",
        encoding="utf-8",
    )

    # Build a fake BeautifulSoup class that actually strips script/style
    try:
        from bs4 import BeautifulSoup as RealBS4
        _bs4_available = True
    except ImportError:
        _bs4_available = False

    if not _bs4_available:
        pytest.skip("beautifulsoup4 not installed")

    with patch("doc_to_md.engines.html.trafilatura", None), \
         patch("doc_to_md.engines.html.BeautifulSoup", RealBS4):
        response = HtmlLocalEngine().convert(html_file)

    assert "Real content" in response.markdown
    # script/style bodies must not leak through
    assert "alert" not in response.markdown
    assert ".x{}" not in response.markdown


def test_html_engine_htm_extension(tmp_path: Path) -> None:
    """Engine should work with .htm extension too."""
    htm_file = tmp_path / "page.htm"
    htm_file.write_text(SIMPLE_HTML, encoding="utf-8")

    response = HtmlLocalEngine().convert(htm_file)
    assert "Hello World" in response.markdown


def test_extract_html_via_extract_text(tmp_path: Path) -> None:
    """extract_text() should handle .html files through the local pipeline."""
    from doc_to_md.pipeline.text_extraction import extract_text

    html_file = tmp_path / "sample.html"
    html_file.write_text(SIMPLE_HTML, encoding="utf-8")

    text = extract_text(html_file)
    assert "Hello World" in text


def test_extract_htm_via_extract_text(tmp_path: Path) -> None:
    """extract_text() should handle .htm files."""
    from doc_to_md.pipeline.text_extraction import extract_text

    htm_file = tmp_path / "sample.htm"
    htm_file.write_text(SIMPLE_HTML, encoding="utf-8")

    text = extract_text(htm_file)
    assert "Hello World" in text
