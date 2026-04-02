import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from doc_to_md.api import app
from doc_to_md.apps.conversion.logic import ConversionRun, RunMetrics
from doc_to_md.apps.conversion import router as conversion_router


client = TestClient(app)


def test_api_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_conversion_engines_endpoint() -> None:
    response = client.get("/apps/conversion/engines")
    assert response.status_code == 200
    payload = response.json()
    assert "engines" in payload
    assert "local" in payload["engines"]


def test_conversion_endpoint_forwards_no_page_info(monkeypatch, tmp_path) -> None:
    captured: dict[str, object] = {}

    def fake_run_conversion(**kwargs):
        captured.update(kwargs)
        return ConversionRun(
            engine="mistral",
            model="mistral-ocr-latest",
            input_dir=tmp_path / "input",
            output_dir=tmp_path / "output",
            metrics=RunMetrics(),
            duration_seconds=0.01,
            results=[],
        )

    monkeypatch.setattr(conversion_router, "run_conversion", fake_run_conversion)

    response = client.post(
        "/apps/conversion/convert",
        json={
            "input_path": str(tmp_path / "input"),
            "output_path": str(tmp_path / "output"),
            "engine": "mistral",
            "no_page_info": True,
            "dry_run": True,
        },
    )

    assert response.status_code == 200
    assert captured["no_page_info"] is True
