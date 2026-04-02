from doc_to_md.config.settings import Settings
from doc_to_md.engines.base import EngineAsset
from doc_to_md.pipeline.formula_ocr import replace_formula_images
from doc_to_md.pipeline.postprocessor import ConversionResult, enforce_markdown


class _FakeFormulaClient:
    def __init__(self, responses: dict[str, str | None]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, str]] = []

    def transcribe(self, asset: EngineAsset, *, mode: str, context: str) -> str | None:
        self.calls.append((asset.filename, mode))
        return self.responses.get(asset.filename)


def _settings(tmp_path, *, enabled: bool = True) -> Settings:
    return Settings(
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
        formula_ocr_enabled=enabled,
    )


def test_replace_formula_images_rewrites_standalone_formula(tmp_path) -> None:
    settings = _settings(tmp_path)
    client = _FakeFormulaClient({"imageFile1.png": "$$MC = A + B$$"})
    result = ConversionResult(
        source_name="sample.pdf",
        markdown="计算公式如下：\n\n![image 1](sample_images/imageFile1.png)\n\n其中：MC 为最低资本。",
        engine="opendataloader",
        assets=[EngineAsset(filename="imageFile1.png", data=b"png-bytes", subdir="sample_images")],
    )

    cleaned = replace_formula_images(result, settings=settings, client=client)

    assert "$$MC = A + B$$" in cleaned.markdown
    assert "![image 1]" not in cleaned.markdown
    assert cleaned.assets == []
    assert client.calls == [("imageFile1.png", "block")]


def test_replace_formula_images_rewrites_table_cells_as_inline_math(tmp_path) -> None:
    settings = _settings(tmp_path)
    client = _FakeFormulaClient({"imageFile2.png": "MC\n非寿险保险"})
    result = ConversionResult(
        source_name="sample.pdf",
        markdown=(
            "|相关系数|![image 2](sample_images/imageFile2.png)|1|\n"
            "|---|---|---|\n"
            "|1|0.1|0.2|"
        ),
        engine="opendataloader",
        assets=[EngineAsset(filename="imageFile2.png", data=b"png-bytes", subdir="sample_images")],
    )

    cleaned = replace_formula_images(result, settings=settings, client=client)

    assert "|相关系数|$MC_{非寿险保险}$|1|" in cleaned.markdown
    assert cleaned.assets == []
    assert client.calls == [("imageFile2.png", "inline")]


def test_replace_formula_images_keeps_original_when_ocr_fails(tmp_path) -> None:
    settings = _settings(tmp_path)
    client = _FakeFormulaClient({"imageFile1.png": None})
    result = ConversionResult(
        source_name="sample.pdf",
        markdown="计算公式如下：\n\n![image 1](sample_images/imageFile1.png)",
        engine="opendataloader",
        assets=[EngineAsset(filename="imageFile1.png", data=b"png-bytes", subdir="sample_images")],
    )

    cleaned = replace_formula_images(result, settings=settings, client=client)

    assert cleaned.markdown == result.markdown
    assert cleaned.assets == result.assets


def test_enforce_markdown_runs_formula_ocr_when_enabled(tmp_path, monkeypatch) -> None:
    settings = _settings(tmp_path)
    marker = {"called": False}

    def _fake_replace(result: ConversionResult, *, settings: Settings, client=None) -> ConversionResult:
        marker["called"] = True
        return ConversionResult(
            source_name=result.source_name,
            markdown="cleaned body",
            engine=result.engine,
            assets=result.assets,
        )

    monkeypatch.setattr("doc_to_md.pipeline.postprocessor.get_settings", lambda: settings)
    monkeypatch.setattr("doc_to_md.pipeline.postprocessor.replace_formula_images", _fake_replace)

    cleaned = enforce_markdown(
        ConversionResult(
            source_name="sample.pdf",
            markdown="  body with spaces  ",
            engine="opendataloader",
            assets=[],
        )
    )

    assert marker["called"] is True
    assert cleaned.markdown == "cleaned body"
