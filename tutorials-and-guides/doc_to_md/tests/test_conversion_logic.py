from pathlib import Path

from doc_to_md.apps.conversion.logic import list_engine_names, run_conversion


def test_list_engine_names_contains_core_engines() -> None:
    engines = list_engine_names()
    assert "local" in engines
    assert "mistral" in engines
    assert "markitdown" in engines


def test_run_conversion_dry_run(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    (input_dir / "sample.txt").write_text("hello", encoding="utf-8")

    summary = run_conversion(
        input_path=input_dir,
        output_path=output_dir,
        engine="local",
        dry_run=True,
    )

    assert summary.metrics.total_candidates == 1
    assert summary.metrics.dry_run == 1
    assert summary.metrics.successes == 0
    assert summary.results[0].status == "dry_run"


def test_run_conversion_local_writes_markdown(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    (input_dir / "sample.txt").write_text("hello markdown", encoding="utf-8")

    summary = run_conversion(
        input_path=input_dir,
        output_path=output_dir,
        engine="local",
    )

    assert summary.metrics.successes == 1
    assert summary.results[0].output_path is not None
    assert summary.results[0].output_path.exists()
