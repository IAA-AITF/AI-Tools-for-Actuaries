"""Pydantic models for the conversion FastAPI app."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ConvertRequest(BaseModel):
    input_path: str | None = Field(default=None, description="Directory of input documents")
    output_path: str | None = Field(default=None, description="Directory where Markdown files should be written")
    engine: str | None = Field(default=None, description="Engine name override")
    model: str | None = Field(default=None, description="Model override for engines that support it")
    since: datetime | None = Field(default=None, description="Process only files modified on or after this timestamp")
    no_page_info: bool = Field(default=False, description="Disable page headings and footer cleanup when supported by the engine")
    dry_run: bool = Field(default=False, description="List eligible files without converting or writing output")


class DocumentResultResponse(BaseModel):
    source_path: str
    status: str
    output_path: str | None = None
    error: str | None = None
    modified_at: datetime | None = None


class ConvertResponse(BaseModel):
    engine: str
    model: str | None = None
    input_dir: str
    output_dir: str
    total_candidates: int
    eligible: int
    converted: int
    failed: int
    skipped_since: int
    dry_run: int
    duration_seconds: float
    results: list[DocumentResultResponse]


class EnginesResponse(BaseModel):
    engines: list[str]


class HealthResponse(BaseModel):
    status: str = "ok"
