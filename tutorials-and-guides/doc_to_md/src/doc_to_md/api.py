"""FastAPI entrypoint for doc_to_md."""
from __future__ import annotations

from typing import Any

from doc_to_md import __version__

_FASTAPI_IMPORT_ERROR: ImportError | None = None

try:
    from fastapi import FastAPI
except ImportError as exc:  # pragma: no cover - optional dependency
    FastAPI = Any  # type: ignore[assignment]
    _FASTAPI_IMPORT_ERROR = exc


def create_app() -> FastAPI:
    if _FASTAPI_IMPORT_ERROR is not None:
        raise RuntimeError(
            "FastAPI support requires optional dependencies. "
            "Install them with `pip install \".[api]\"` before importing the API app."
        ) from _FASTAPI_IMPORT_ERROR

    from doc_to_md.apps.conversion.router import router as conversion_router

    app = FastAPI(
        title="doc_to_md API",
        version=__version__,
        description="HTTP interface for document-to-markdown conversion apps.",
    )
    app.include_router(conversion_router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app() if _FASTAPI_IMPORT_ERROR is None else None


def run() -> None:
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "FastAPI support requires optional dependencies. "
            "Install them with `pip install \".[api]\"` before running the API server."
        ) from exc

    if app is None:
        raise RuntimeError(
            "FastAPI support requires optional dependencies. "
            "Install them with `pip install \".[api]\"` before running the API server."
        ) from _FASTAPI_IMPORT_ERROR

    uvicorn.run("doc_to_md.api:app", host="127.0.0.1", port=8000, reload=False)
