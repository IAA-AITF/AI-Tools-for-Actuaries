from datetime import datetime, timedelta
from pathlib import Path

from doc_to_md.apps.conversion.logic import RunMetrics, _format_summary, _should_process


def test_should_process_without_since(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("data", encoding="utf-8")
    should_process, mtime = _should_process(file_path, None)
    assert should_process is True
    assert isinstance(mtime, float)


def test_should_process_with_since_filter(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("data", encoding="utf-8")
    threshold = datetime.fromtimestamp(file_path.stat().st_mtime) + timedelta(seconds=10)
    should_process, _ = _should_process(file_path, threshold.timestamp())
    assert should_process is False


def test_format_summary() -> None:
    metrics = RunMetrics(
        total_candidates=5,
        skipped_by_since=2,
        dry_run=1,
        successes=2,
        failures=1,
    )
    summary = _format_summary(metrics, elapsed_seconds=12.34)
    assert "total=5" in summary
    assert "eligible=3" in summary
    assert "converted=2" in summary
    assert summary.endswith("12.34s")
