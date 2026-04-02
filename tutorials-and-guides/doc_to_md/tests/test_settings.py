from pathlib import Path

import pytest

from doc_to_md.config.settings import Settings


def test_settings_allows_remote_default_without_secret(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)

    settings = Settings(
        default_engine="mistral",
        mistral_api_key=None,
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
    )

    assert settings.default_engine == "mistral"
    assert settings.input_dir.exists()
    assert settings.output_dir.exists()


def test_package_settings_module_is_importable() -> None:
    from doc_to_md.config import settings

    assert settings.Settings.__name__ == "Settings"
