"""Post-processing helpers after engine response."""
from __future__ import annotations

from dataclasses import dataclass
import html
import re

from doc_to_md.config.settings import get_settings
from doc_to_md.engines.base import EngineAsset
from doc_to_md.pipeline.formula_ocr import replace_formula_images


@dataclass(slots=True)
class ConversionResult:
    source_name: str
    markdown: str
    engine: str
    assets: list[EngineAsset]


MATH_SEGMENT_PATTERN = re.compile(
    r"(?P<display_dollar>\$\$.*?\$\$)"
    r"|(?P<display_bracket>\\\[.*?\\\])"
    r"|(?P<inline_paren>\\\(.*?\\\))"
    r"|(?P<inline_dollar>(?<!\$)\$(?!\$).*?(?<!\\)\$)",
    re.DOTALL,
)

ENTITY_REPLACEMENTS = (
    (re.compile(r"&\s*lt;", re.IGNORECASE), "<"),
    (re.compile(r"&\s*gt;", re.IGNORECASE), ">"),
    (re.compile(r"&\s*amp;", re.IGNORECASE), "&"),
)

MATH_OPERATOR_SPACING_PATTERN = re.compile(r"(?<!\\)[ \t]*([_^])[ \t]*")

BROKEN_CJK_SUBSUP_WITH_INDEX_PATTERN = re.compile(
    r"(?P<op>[_^])\s*\{\s*\\(?P<label>[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+)\s*_(?P<index>[A-Za-z0-9]+)\s*\}"
)

BROKEN_CJK_SUBSUP_PATTERN = re.compile(
    r"(?P<op>[_^])\s*\{\s*\\(?P<label>[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+)\s*\}"
)


def enforce_markdown(result: ConversionResult) -> ConversionResult:
    """Placeholder hook to normalize Markdown (e.g., strip trailing spaces)."""
    cleaned = result.markdown.strip()
    normalized = ConversionResult(
        source_name=result.source_name,
        markdown=normalize_math_entities(cleaned),
        engine=result.engine,
        assets=result.assets,
    )
    settings = get_settings()
    if settings.formula_ocr_enabled:
        normalized = replace_formula_images(normalized, settings=settings)
        return ConversionResult(
            source_name=normalized.source_name,
            markdown=normalize_math_entities(normalized.markdown),
            engine=normalized.engine,
            assets=normalized.assets,
        )
    return normalized


def normalize_math_entities(markdown: str) -> str:
    return MATH_SEGMENT_PATTERN.sub(lambda match: _decode_math_entities(match.group(0)), markdown)


def _decode_math_entities(segment: str) -> str:
    cleaned = segment
    for pattern, replacement in ENTITY_REPLACEMENTS:
        cleaned = pattern.sub(replacement, cleaned)
    for _ in range(3):
        unescaped = html.unescape(cleaned)
        if unescaped == cleaned:
            break
        cleaned = unescaped
    cleaned = BROKEN_CJK_SUBSUP_WITH_INDEX_PATTERN.sub(_replace_broken_cjk_subsup_with_index, cleaned)
    cleaned = BROKEN_CJK_SUBSUP_PATTERN.sub(_replace_broken_cjk_subsup, cleaned)
    cleaned = _normalize_math_operator_spacing(cleaned)
    return cleaned.replace("\xa0", " ")


def _normalize_math_operator_spacing(segment: str) -> str:
    return MATH_OPERATOR_SPACING_PATTERN.sub(r" \1 ", segment)


def _replace_broken_cjk_subsup_with_index(match: re.Match[str]) -> str:
    op = match.group("op")
    label = match.group("label")
    index = match.group("index")
    return f"{op}{{\\text{{{label}}}_{index}}}"


def _replace_broken_cjk_subsup(match: re.Match[str]) -> str:
    op = match.group("op")
    label = match.group("label")
    return f"{op}{{\\text{{{label}}}}}"
