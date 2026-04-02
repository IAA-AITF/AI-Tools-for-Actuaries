from types import SimpleNamespace
from unittest.mock import patch

from doc_to_md.engines.mistral import MistralEngine


class _FakeMistralClient:
    def __init__(self, *args, **kwargs) -> None:
        pass


def _mock_settings() -> SimpleNamespace:
    return SimpleNamespace(
        mistral_api_key="test-key",
        mistral_default_model="mistral-ocr-latest",
        mistral_timeout_seconds=60.0,
        mistral_retry_attempts=3,
        mistral_max_pdf_tokens=9000,
        mistral_max_pages_per_chunk=25,
    )


def test_mistral_omits_page_headers_by_default() -> None:
    with patch("doc_to_md.engines.mistral.get_settings", return_value=_mock_settings()), patch(
        "doc_to_md.engines.mistral.Mistral", _FakeMistralClient
    ):
        engine = MistralEngine()

    assert engine.include_page_headers is False


def test_strip_page_artifacts_removes_page_headers_and_standalone_page_numbers() -> None:
    text = "\n".join(
        [
            "正文第一段",
            "",
            "## Page 2",
            "2",
            "正文第二段",
            "- 3 -",
            "Page 4",
            "正文第三段",
        ]
    )

    cleaned = MistralEngine._strip_page_artifacts(text)

    assert "## Page 2" not in cleaned
    assert "\n2\n" not in f"\n{cleaned}\n"
    assert "- 3 -" not in cleaned
    assert "Page 4" not in cleaned
    assert "正文第一段" in cleaned
    assert "正文第二段" in cleaned
    assert "正文第三段" in cleaned
