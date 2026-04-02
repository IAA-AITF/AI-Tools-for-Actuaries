from doc_to_md.config.settings import Settings


def test_settings_formula_ocr_defaults(tmp_path) -> None:
    settings = Settings(
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
    )

    assert settings.formula_ocr_enabled is False
    assert settings.formula_ocr_provider == "mistral"
