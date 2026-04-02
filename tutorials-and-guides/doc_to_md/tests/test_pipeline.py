from pathlib import Path

import pytest
from doc_to_md.pipeline import text_extraction
from doc_to_md.pipeline.loader import iter_documents


def test_iter_documents(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "b.bin").write_text("ignore", encoding="utf-8")
    files = list(iter_documents(tmp_path))
    assert len(files) == 1
    assert files[0].name == "a.txt"


def test_extract_text_docx(tmp_path: Path) -> None:
    docx = pytest.importorskip("docx")
    doc = docx.Document()
    doc.add_paragraph("Hello DOCX")
    doc.add_paragraph("Another line")
    doc.save(tmp_path / "sample.docx")

    text = text_extraction.extract_text(tmp_path / "sample.docx")
    assert "Hello DOCX" in text
    assert "Another line" in text


def test_extract_text_image(monkeypatch, tmp_path: Path) -> None:
    PIL = pytest.importorskip("PIL.Image")
    image_path = tmp_path / "image.png"
    PIL.new("RGB", (10, 10), color="white").save(image_path)

    class _FakeTesseract:
        @staticmethod
        def image_to_string(_image):
            return "detected text"

    monkeypatch.setattr(text_extraction, "pytesseract", _FakeTesseract())

    text = text_extraction.extract_text(image_path)
    assert text == "detected text"
