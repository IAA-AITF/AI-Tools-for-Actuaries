"""Replace formula-like image references with Markdown math."""
from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Protocol

from doc_to_md.config.settings import Settings, get_settings
from doc_to_md.engines.base import EngineAsset, RetryableRequestMixin
from doc_to_md.utils.logging import log_warning

IMAGE_RE = re.compile(r"!\[[^\]]*]\(([^)]+)\)")
FORMULA_KEYWORDS = ("公式", "计算公式", "如下", "其中", "矩阵", "相关系数", "min", "max")
MATH_HINTS = ("\\", "=", "_", "^", "{", "}", "sqrt", "min", "max", "sum", "prod")


class FormulaOcrClient(Protocol):
    def transcribe(self, asset: EngineAsset, *, mode: str, context: str) -> str | None:
        ...


class _MistralFormulaOcrClient(RetryableRequestMixin):
    def __init__(self, settings: Settings) -> None:
        if not settings.mistral_api_key:
            raise RuntimeError("MISTRAL_API_KEY missing")
        super().__init__(retry_attempts=settings.mistral_retry_attempts)
        self.api_key = settings.mistral_api_key
        self.model = settings.mistral_default_model
        self.timeout_ms = int(settings.mistral_timeout_seconds * 1000)
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from mistralai import Mistral

            self._client = Mistral(api_key=self.api_key, timeout_ms=self.timeout_ms)
        return self._client

    def transcribe(self, asset: EngineAsset, *, mode: str, context: str) -> str | None:
        del mode, context
        upload = self._request_with_retry(
            lambda: self.client.files.upload(
                file={"file_name": asset.filename, "content": asset.data},
                purpose="ocr",
            ),
            operation=f"formula_ocr_mistral_upload_{asset.filename}",
        )
        try:
            response = self._request_with_retry(
                lambda: self.client.ocr.process(
                    model=self.model,
                    document={"type": "file", "file_id": upload.id},
                    include_image_base64=False,
                ),
                operation=f"formula_ocr_mistral_process_{asset.filename}",
            )
            pages = [page.markdown.strip() for page in response.pages if page.markdown and page.markdown.strip()]
            return "\n".join(pages).strip() or None
        finally:
            try:
                self.client.files.delete(file_id=upload.id)
            except Exception:
                pass


class _DeepSeekFormulaOcrClient(RetryableRequestMixin):
    _PROMPT = (
        "Transcribe this document snippet into Markdown math. "
        "If it is a standalone formula, return only a $$...$$ block. "
        "If it is a table or matrix label, return only inline math or short plain text. "
        "Do not explain."
    )

    def __init__(self, settings: Settings) -> None:
        if not settings.siliconflow_api_key:
            raise RuntimeError("SILICONFLOW_API_KEY missing")
        super().__init__(retry_attempts=settings.siliconflow_retry_attempts)
        self.api_key = settings.siliconflow_api_key
        self.base_url = settings.siliconflow_base_url
        self.model = settings.siliconflow_default_model
        self.timeout = settings.siliconflow_timeout_seconds
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def transcribe(self, asset: EngineAsset, *, mode: str, context: str) -> str | None:
        payload = base64.b64encode(asset.data).decode("utf-8")
        prompt = self._PROMPT
        if mode == "inline":
            prompt += " Prefer inline math for short labels."
        if context.strip():
            prompt += f"\n\nContext:\n{context.strip()}"
        completion = self._request_with_retry(
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an OCR model specialized in formulas and table symbols.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{payload}",
                                    "detail": "high",
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    },
                ],
                timeout=self.timeout,
                max_tokens=300,
                temperature=0.0,
            ),
            operation=f"formula_ocr_deepseek_{asset.filename}",
        )
        if not completion.choices:
            return None
        content = completion.choices[0].message.content
        return content.strip() if isinstance(content, str) and content.strip() else None


def replace_formula_images(
    result,
    *,
    settings: Settings | None = None,
    client: FormulaOcrClient | None = None,
):
    active_settings = settings or get_settings()
    if not active_settings.formula_ocr_enabled:
        return result
    if not result.assets or "![" not in result.markdown:
        return result

    try:
        formula_client = client or _build_client(active_settings)
    except Exception as exc:
        log_warning(f"Formula OCR disabled for {result.source_name}: {exc}")
        return result

    assets_by_name: dict[str, EngineAsset] = {}
    for asset in result.assets:
        assets_by_name.setdefault(asset.filename, asset)

    lines = result.markdown.splitlines()
    replaced_filenames: set[str] = set()
    cache: dict[str, str | None] = {}

    for index, line in enumerate(lines):
        matches = list(IMAGE_RE.finditer(line))
        if not matches:
            continue
        if not _should_attempt_formula_replacement(lines, index):
            continue

        rebuilt: list[str] = []
        cursor = 0
        replacement_made = False
        for match in matches:
            rebuilt.append(line[cursor:match.start()])
            token = match.group(0)
            reference = match.group(1)
            filename = Path(reference).name
            asset = assets_by_name.get(filename)
            replacement = token
            if asset is not None:
                mode = _replacement_mode(line, token)
                if filename not in cache:
                    context = _context_window(lines, index)
                    raw_text = formula_client.transcribe(asset, mode=mode, context=context)
                    cache[filename] = _normalize_formula_text(raw_text, mode=mode)
                normalized = cache[filename]
                if normalized:
                    replacement = normalized
                    replacement_made = True
                    replaced_filenames.add(filename)
            rebuilt.append(replacement)
            cursor = match.end()

        rebuilt.append(line[cursor:])
        if replacement_made:
            lines[index] = "".join(rebuilt)

    cleaned_markdown = "\n".join(lines).strip()
    cleaned_assets = [asset for asset in result.assets if asset.filename not in replaced_filenames]
    return result.__class__(
        source_name=result.source_name,
        markdown=cleaned_markdown,
        engine=result.engine,
        assets=cleaned_assets,
    )


def _build_client(settings: Settings) -> FormulaOcrClient:
    if settings.formula_ocr_provider == "deepseekocr":
        return _DeepSeekFormulaOcrClient(settings)
    return _MistralFormulaOcrClient(settings)


def _should_attempt_formula_replacement(lines: list[str], index: int) -> bool:
    line = lines[index]
    if "|" in line and "---" not in line:
        return True
    tokens = list(IMAGE_RE.finditer(line))
    if len(tokens) == 1 and line.strip() == tokens[0].group(0):
        return True
    window = _context_window(lines, index).lower()
    return any(keyword.lower() in window for keyword in FORMULA_KEYWORDS)


def _context_window(lines: list[str], index: int, radius: int = 1) -> str:
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    return "\n".join(lines[start:end])


def _replacement_mode(line: str, token: str) -> str:
    if "|" in line and "---" not in line:
        return "inline"
    if line.strip() == token:
        return "block"
    return "inline"


def _normalize_formula_text(raw_text: str | None, *, mode: str) -> str | None:
    if not raw_text:
        return None
    cleaned = _strip_code_fences(raw_text).replace("\r\n", "\n").strip()
    if not cleaned:
        return None
    if mode == "inline":
        return _normalize_inline_formula(cleaned)
    return _normalize_block_formula(cleaned)


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped


def _normalize_inline_formula(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("$$") and stripped.endswith("$$"):
        stripped = stripped[2:-2].strip()
    elif stripped.startswith("$") and stripped.endswith("$"):
        return stripped

    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if len(lines) == 2 and _looks_like_variable(lines[0]) and _looks_like_descriptor(lines[1]):
        descriptor = "".join(lines[1].split())
        return f"${lines[0]}_{{{descriptor}}}$"

    one_line = " ".join(lines) if lines else stripped
    if one_line.startswith("$") and one_line.endswith("$"):
        return one_line
    if _looks_like_math(one_line):
        return f"${one_line}$"
    return one_line


def _normalize_block_formula(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("$$") and stripped.endswith("$$"):
        return stripped
    if stripped.startswith("$") and stripped.endswith("$"):
        inner = stripped[1:-1].strip()
        return f"$$\n{inner}\n$$"

    inline_candidate = _normalize_inline_formula(stripped)
    if inline_candidate.startswith("$") and inline_candidate.endswith("$") and "\n" not in inline_candidate:
        return inline_candidate

    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    one_line = " ".join(lines) if lines else stripped
    if _looks_like_math(one_line):
        return f"$$\n{one_line}\n$$"
    return stripped


def _looks_like_variable(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9*^+-]*", text))


def _looks_like_descriptor(text: str) -> bool:
    condensed = "".join(text.split())
    if not condensed:
        return False
    return any("\u4e00" <= char <= "\u9fff" for char in condensed) or condensed.isalpha()


def _looks_like_math(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in MATH_HINTS)
