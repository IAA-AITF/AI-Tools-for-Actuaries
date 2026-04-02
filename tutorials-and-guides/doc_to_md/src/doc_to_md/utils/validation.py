"""Input validation utilities for document processing."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

# File size limits (in bytes)
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Supported file extensions
SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt", ".md", ".docx", ".html", ".htm", ".pptx", ".xlsx"}

FileValidationError = type("FileValidationError", (ValueError,), {})


def validate_file(path: Path) -> Literal[True]:
    """
    Validate that a file is suitable for processing.
    
    Args:
        path: Path to the file to validate
        
    Returns:
        True if validation passes
        
    Raises:
        FileValidationError: If validation fails
    """
    # Check file exists
    if not path.exists():
        raise FileValidationError(f"File does not exist: {path}")
    
    # Check it's a file, not a directory
    if not path.is_file():
        raise FileValidationError(f"Path is not a file: {path}")
    
    # Check file extension
    suffix = path.suffix.lower()
    
    # Check for .doc format (not supported, only .docx) before generic check
    if suffix == ".doc":
        raise FileValidationError(
            "Legacy .doc format is not supported. "
            "Please convert to .docx format first."
        )
    
    if suffix not in SUPPORTED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file format: {suffix}. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    
    # Check file size
    try:
        file_size = path.stat().st_size
    except OSError as exc:
        raise FileValidationError(f"Cannot read file stats: {exc}") from exc
    
    if file_size == 0:
        raise FileValidationError(f"File is empty: {path}")
    
    if file_size > MAX_FILE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        raise FileValidationError(
            f"File too large: {size_mb:.1f}MB exceeds limit of {MAX_FILE_SIZE_MB}MB"
        )
    
    # Check file is readable
    try:
        with path.open("rb") as f:
            # Try to read first few bytes to ensure file is readable
            f.read(10)
    except OSError as exc:
        raise FileValidationError(f"File is not readable: {exc}") from exc
    
    return True


def is_likely_corrupted_pdf(path: Path) -> bool:
    """
    Check if a PDF file is likely corrupted by examining its header.
    
    Args:
        path: Path to PDF file
        
    Returns:
        True if file appears corrupted
    """
    try:
        with path.open("rb") as f:
            header = f.read(5)
            # PDF files should start with %PDF-
            if not header.startswith(b"%PDF-"):
                return True
    except Exception:  # noqa: BLE001
        return True
    return False


def is_likely_corrupted_docx(path: Path) -> bool:
    """
    Check if a DOCX file is likely corrupted by examining its structure.
    
    Args:
        path: Path to DOCX file
        
    Returns:
        True if file appears corrupted
    """
    try:
        import zipfile
        # DOCX files are ZIP archives
        if not zipfile.is_zipfile(path):
            return True
    except Exception:  # noqa: BLE001
        return True
    return False
