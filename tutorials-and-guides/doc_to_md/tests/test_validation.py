"""Tests for input validation utilities."""
from pathlib import Path

import pytest

from doc_to_md.utils.validation import (
    FileValidationError,
    MAX_FILE_SIZE_BYTES,
    validate_file,
    is_likely_corrupted_pdf,
    is_likely_corrupted_docx,
)


def test_validate_file_success(tmp_path: Path) -> None:
    """Test validation passes for valid file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("Hello, world!", encoding="utf-8")
    
    assert validate_file(file_path) is True


def test_validate_file_not_exists(tmp_path: Path) -> None:
    """Test validation fails for non-existent file."""
    file_path = tmp_path / "nonexistent.txt"
    
    with pytest.raises(FileValidationError, match="does not exist"):
        validate_file(file_path)


def test_validate_file_is_directory(tmp_path: Path) -> None:
    """Test validation fails for directory."""
    with pytest.raises(FileValidationError, match="not a file"):
        validate_file(tmp_path)


def test_validate_file_unsupported_extension(tmp_path: Path) -> None:
    """Test validation fails for unsupported file extension."""
    file_path = tmp_path / "test.xyz"
    file_path.write_text("content", encoding="utf-8")
    
    with pytest.raises(FileValidationError, match="Unsupported file format"):
        validate_file(file_path)


def test_validate_file_legacy_doc_format(tmp_path: Path) -> None:
    """Test validation fails for .doc format with helpful message."""
    file_path = tmp_path / "test.doc"
    file_path.write_bytes(b"fake doc content")
    
    with pytest.raises(FileValidationError, match="Legacy .doc format"):
        validate_file(file_path)


def test_validate_file_empty(tmp_path: Path) -> None:
    """Test validation fails for empty file."""
    file_path = tmp_path / "empty.txt"
    file_path.touch()
    
    with pytest.raises(FileValidationError, match="File is empty"):
        validate_file(file_path)


def test_validate_file_too_large(tmp_path: Path) -> None:
    """Test validation fails for file exceeding size limit."""
    # Create file slightly over limit
    # Since we can't easily mock Path.stat, test with file just over the acceptable size
    # This test validates the check exists, actual size testing can be done in integration
    file_path = tmp_path / "test.txt"
    file_path.write_text("x", encoding="utf-8")  # Small file that will pass
    
    # Instead, let's test with an artificially large file
    # Skip this test if we can't create large files
    try:
        large_content = b"x" * (MAX_FILE_SIZE_BYTES + 1)
        file_path.write_bytes(large_content)
        
        with pytest.raises(FileValidationError, match="File too large"):
            validate_file(file_path)
    except (OSError, MemoryError):
        # Can't create file that large in test environment, skip
        pytest.skip("Cannot create large file for testing")


def test_validate_file_not_readable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test validation handles unreadable files."""
    file_path = tmp_path / "unreadable.txt"
    file_path.write_text("content", encoding="utf-8")

    original_open = Path.open

    def fake_open(self: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
        if self == file_path:
            raise OSError("permission denied")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)

    with pytest.raises(FileValidationError, match="File is not readable"):
        validate_file(file_path)


def test_is_likely_corrupted_pdf_valid(tmp_path: Path) -> None:
    """Test PDF corruption detection for valid PDF."""
    file_path = tmp_path / "test.pdf"
    file_path.write_bytes(b"%PDF-1.4\n%content")
    
    assert not is_likely_corrupted_pdf(file_path)


def test_is_likely_corrupted_pdf_invalid(tmp_path: Path) -> None:
    """Test PDF corruption detection for invalid PDF."""
    file_path = tmp_path / "test.pdf"
    file_path.write_bytes(b"not a pdf file")
    
    assert is_likely_corrupted_pdf(file_path)


def test_is_likely_corrupted_docx_valid(tmp_path: Path) -> None:
    """Test DOCX corruption detection for valid DOCX."""
    import zipfile
    
    file_path = tmp_path / "test.docx"
    with zipfile.ZipFile(file_path, "w") as zf:
        zf.writestr("document.xml", "<document/>")
    
    assert not is_likely_corrupted_docx(file_path)


def test_is_likely_corrupted_docx_invalid(tmp_path: Path) -> None:
    """Test DOCX corruption detection for invalid DOCX."""
    file_path = tmp_path / "test.docx"
    file_path.write_bytes(b"not a docx file")
    
    assert is_likely_corrupted_docx(file_path)
