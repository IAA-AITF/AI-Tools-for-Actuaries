"""FastAPI router for the conversion app."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from doc_to_md.apps.conversion.logic import list_engine_names, run_conversion
from doc_to_md.apps.conversion.schemas import (
    ConvertRequest,
    ConvertResponse,
    DocumentResultResponse,
    EnginesResponse,
    HealthResponse,
)

router = APIRouter(prefix="/apps/conversion", tags=["conversion"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.get("/engines", response_model=EnginesResponse)
def list_engines() -> EnginesResponse:
    return EnginesResponse(engines=list_engine_names())


@router.post("/convert", response_model=ConvertResponse)
def convert_documents(payload: ConvertRequest) -> ConvertResponse:
    try:
        summary = run_conversion(
            input_path=payload.input_path,
            output_path=payload.output_path,
            engine=payload.engine,
            model=payload.model,
            since=payload.since,
            no_page_info=payload.no_page_info,
            dry_run=payload.dry_run,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ConvertResponse(
        engine=summary.engine,
        model=summary.model,
        input_dir=str(summary.input_dir),
        output_dir=str(summary.output_dir),
        total_candidates=summary.metrics.total_candidates,
        eligible=summary.metrics.eligible,
        converted=summary.metrics.successes,
        failed=summary.metrics.failures,
        skipped_since=summary.metrics.skipped_by_since,
        dry_run=summary.metrics.dry_run,
        duration_seconds=summary.duration_seconds,
        results=[
            DocumentResultResponse(
                source_path=str(item.source_path),
                status=item.status,
                output_path=str(item.output_path) if item.output_path else None,
                error=item.error,
                modified_at=item.modified_at,
            )
            for item in summary.results
        ],
    )
