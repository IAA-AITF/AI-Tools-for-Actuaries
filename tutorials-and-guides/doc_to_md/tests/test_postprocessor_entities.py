from doc_to_md.pipeline.postprocessor import ConversionResult, enforce_markdown, normalize_math_entities


def test_normalize_math_entities_decodes_only_math_segments() -> None:
    text = "t 为年度，$20 &lt; t \\leq 40$；正文里保留 &lt; 文本。"

    cleaned = normalize_math_entities(text)

    assert "$20 < t \\leq 40$" in cleaned
    assert "正文里保留 &lt; 文本" in cleaned


def test_enforce_markdown_decodes_alignment_entities() -> None:
    result = enforce_markdown(
        ConversionResult(
            source_name="sample.pdf",
            markdown="$$\\begin{cases} 0 &amp; x &lt; 1 \\\\ 1 &amp; x &gt; 1 \\end{cases}$$",
            engine="mistral",
            assets=[],
        )
    )

    assert "&amp;" not in result.markdown
    assert "&lt;" not in result.markdown
    assert "&gt;" not in result.markdown
    assert "\\begin{cases} 0 & x < 1 \\\\ 1 & x > 1 \\end{cases}" in result.markdown


def test_enforce_markdown_repairs_broken_cjk_subscripts() -> None:
    result = enforce_markdown(
        ConversionResult(
            source_name="sample.pdf",
            markdown="$\\mathrm{OL}_{\\巨灾_i}$ $\\mathrm{MC}_{\\客户}$ $\\mathrm{NE}_{\\短期寿险}$",
            engine="mistral",
            assets=[],
        )
    )

    assert "\\mathrm{OL} _ {\\text{巨灾} _ i}" in result.markdown
    assert "\\mathrm{MC} _ {\\text{客户}}" in result.markdown
    assert "\\mathrm{NE} _ {\\text{短期寿险}}" in result.markdown


def test_enforce_markdown_adds_spacing_around_math_subscripts_and_keeps_escaped_underscores() -> None:
    result = enforce_markdown(
        ConversionResult(
            source_name="sample.pdf",
            markdown="正文保留 foo_bar，公式为 $MC_{非寿险保险}$、$x^2$、$\\text{a\\_b}$。",
            engine="mistral",
            assets=[],
        )
    )

    assert "foo_bar" in result.markdown
    assert "$MC _ {非寿险保险}$" in result.markdown
    assert "$x ^ 2$" in result.markdown
    assert "$\\text{a\\_b}$" in result.markdown
