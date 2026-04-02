"""HTML content-extraction engine using trafilatura (primary) and BeautifulSoup (fallback)."""
from __future__ import annotations

import re
from pathlib import Path

from .base import Engine, EngineResponse

try:
    import trafilatura
except ImportError:  # pragma: no cover - optional dependency
    trafilatura = None  # type: ignore[assignment]

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover - optional dependency
    BeautifulSoup = None  # type: ignore[assignment]


class HtmlLocalEngine(Engine):
    """Extract the main readable content from an HTML document.

    Strategy (in order of preference):
    1. ``trafilatura`` — purpose-built web content extractor.  Best at stripping
       navigation, ads, footers and returning only the article body.
    2. ``beautifulsoup4`` — generic HTML parser that removes script/style nodes and
       returns clean text.  Installed via the ``html`` extra.
    3. Plain regex tag-stripping — last-resort fallback that requires no libraries.
    """

    name = "html_local"

    def convert(self, path: Path) -> EngineResponse:
        raw_html = path.read_text(encoding="utf-8", errors="replace")

        markdown = (
            self._extract_with_trafilatura(raw_html)
            or self._extract_with_bs4(raw_html)
            or self._extract_with_regex(raw_html)
        )

        if not markdown.strip():
            markdown = "_No readable content could be extracted from HTML._"

        return EngineResponse(
            markdown=f"# {path.stem}\n\n{markdown}\n",
            model="html-local",
        )

    # ------------------------------------------------------------------
    # Extraction strategies
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_with_trafilatura(html: str) -> str | None:
        """Use trafilatura to extract the main content as Markdown."""
        if trafilatura is None:
            return None
        try:
            result = trafilatura.extract(
                html,
                output_format="markdown",
                include_comments=False,
                include_tables=True,
                no_fallback=False,
            )
            return result or None
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _extract_with_bs4(html: str) -> str | None:
        """Use BeautifulSoup to strip tags and return clean text."""
        if BeautifulSoup is None:
            return None
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Remove boilerplate elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                tag.decompose()

            text = soup.get_text(separator="\n")
            # Collapse excessive blank lines
            cleaned = re.sub(r"\n{3,}", "\n\n", text).strip()
            return cleaned or None
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _extract_with_regex(html: str) -> str:
        """Last-resort: strip all HTML tags with a simple regex."""
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text
