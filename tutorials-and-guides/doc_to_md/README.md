# doc-to-markdown-converter

Convert PDFs, scans, office documents, HTML, and plain text into LLM-ready Markdown for actuarial document workflows, with a Typer CLI, a FastAPI layer, and pluggable extraction engines.

This repository is designed first for actuaries and actuarial teams working with source documents such as actuarial papers, SFCRs, ORSAs, valuation reports, internal guidance, policy documents, and other materials that need cleanup before indexing, review, chunking, or downstream RAG use.

## Version History

- `0.1.1` (April 1, 2026) - Initial release

## Highlights

- `src/` layout packaged as `doc_to_md`
- Typer CLI with `convert` and `list-engines`
- FastAPI app for HTTP conversion workflows
- Multiple local and remote extraction engines
- Format-aware `auto` engine with per-format routing from `.env`
- Built-in support for PDF, DOCX, PPTX, XLSX, HTML, images, TXT, and Markdown
- Benchmark script for side-by-side engine comparison
- MIT licensed

## Project layout

```text
doc_to_md/
|-- .github/
|   `-- workflows/
|-- benchmark_results/
|-- config/                      # compatibility shim for legacy imports
|-- src/
|   `-- doc_to_md/
|       |-- api.py
|       |-- cli.py
|       |-- apps/
|       |   `-- conversion/
|       |       |-- cli.py
|       |       |-- logic.py
|       |       |-- router.py
|       |       `-- schemas.py
|       |-- config/
|       |   `-- settings.py
|       |-- engines/
|       |-- pipeline/
|       `-- utils/
|-- tests/
|-- tools/
|-- benchmark.py
|-- PDF_ENGINE_EVALUATION.md
|-- README.md
|-- README_BENCHMARK.md
|-- requirements-recommended-pdf.txt
|-- requirements-core.txt
|-- requirements-dev.txt
|-- requirements.txt
`-- pyproject.toml
```

Local working directories such as `data/`, `.venv/`, and temporary `tmp_*` folders are created during use and are not part of the tracked repository layout.

## Python support

- Supported: Python `>=3.10,<3.13`
- Recommended: Python 3.10 or 3.11
- Intentionally unsupported: Python 3.13 and newer

Several optional OCR and ML dependencies lag behind the newest Python releases, so 3.10 or 3.11 remains the safest default.

## Installation

### From a source checkout

```bash
git clone https://github.com/ferryhe/doc_to_md.git
cd doc_to_md

# Windows
py -3.10 -m venv .venv
.venv\Scripts\activate

# Unix/macOS
python3.10 -m venv .venv
source .venv/bin/activate

pip install -e .
```

### Optional extras

Install only the extras you actually need:

```bash
pip install ".[api]"
pip install ".[html]"
pip install ".[office]"
pip install ".[markitdown]"
pip install ".[docling]"
pip install ".[paddleocr]"
pip install ".[mineru]"
pip install ".[marker]"
```

If you are installing from a published package instead of a source checkout, replace `".[extra]"` with `doc-to-markdown-converter[extra]`.

### Install paths

There are now three clear install targets:

| What you want | Use this | Includes |
| --- | --- | --- |
| Current recommended PDF setup | `pip install -r requirements-recommended-pdf.txt` | `local`, `markitdown`, `opendataloader`, `docling`, `mistral` |
| Pinned broad CPU environment | `pip install -r requirements-core.txt` | A wider non-GPU stack including `deepseekocr`, `html_local`, `office`, and `docling` |
| Heavy full stack | `pip install -r requirements.txt` | Adds the GPU-oriented / harder-to-install engines |
| Repo development and tests | `pip install -r requirements-dev.txt` | `pytest`, `fastapi`, `uvicorn`, `ruff`, `build`, `twine` on top of one runtime install |

The current recommended PDF setup is the one that matches the evaluation report.

It keeps:

- `local`
- `markitdown`
- `opendataloader`
- `docling`
- `mistral`

Equivalent direct command:

```bash
# From a source checkout
pip install -e ".[markitdown,docling,opendataloader]"

# From a published package
pip install "doc-to-markdown-converter[markitdown,docling,opendataloader]"
```

Notes for the recommended setup:

- `local` and `mistral` are already included in the base package
- `mistral` does not need an extra, but it does need `MISTRAL_API_KEY`
- `opendataloader` still needs Java 11+ on the system
- on the Windows / Python 3.12 test machine used here, this setup occupied about `1.32 GB` for `.venv` plus about `303 MB` for the JDK

### OpenDataLoader setup

`opendataloader` needs Java 11+ in addition to the Python extra.

1. Install Java 11+.
   Ubuntu or Debian: `sudo apt install default-jre`
   macOS with Homebrew: `brew install openjdk@17`
   Windows: <https://adoptium.net/>

2. Open a new terminal, then verify Java:

```bash
java -version
```

3. Install the Python extra:

```bash
# From a source checkout
pip install -e ".[opendataloader]"

# From a published package
pip install "doc-to-markdown-converter[opendataloader]"
```

4. Run a smoke test:

```bash
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output \
  --engine opendataloader
```

For harder PDFs, set `OPENDATALOADER_HYBRID=docling-fast` before running the same command:

```bash
# Windows PowerShell
$env:OPENDATALOADER_HYBRID="docling-fast"
python -m doc_to_md.cli convert --input-path data/input --output-path data/output --engine opendataloader

# Unix/macOS
OPENDATALOADER_HYBRID=docling-fast \
python -m doc_to_md.cli convert --input-path data/input --output-path data/output --engine opendataloader
```

Common failures:

- `java` not found: restart the terminal or fix Java on `PATH`
- `No module named 'opendataloader_pdf'`: reinstall the extra in the active environment

### Requirements files

Use the requirements files as follows:

```bash
# Current recommended PDF setup
pip install -r requirements-recommended-pdf.txt

# Pinned broad CPU environment
pip install -r requirements-core.txt

# Heavy full stack
pip install -r requirements.txt

# Development and test overlay
pip install -r requirements-dev.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in only the settings you need:

```bash
# Windows
copy .env.example .env

# Unix/macOS
cp .env.example .env
```

Settings are centralized in `doc_to_md.config.settings`.

### Key variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `DEFAULT_ENGINE` | Default engine when `--engine` is omitted | `local` |
| `MISTRAL_API_KEY` | Required for the Mistral OCR engine | unset |
| `SILICONFLOW_API_KEY` | Required for the DeepSeek OCR engine | unset |
| `MISTRAL_DEFAULT_MODEL` | Default Mistral OCR model | `mistral-ocr-latest` |
| `SILICONFLOW_DEFAULT_MODEL` | Default DeepSeek OCR model | `deepseek-ai/DeepSeek-OCR` |
| `AUTO_PDF_ENGINE` | Auto-engine route for PDF | `local` |
| `AUTO_DOCX_ENGINE` | Auto-engine route for DOCX | `local` |
| `AUTO_PPTX_ENGINE` | Auto-engine route for PPTX | `local` |
| `AUTO_SPREADSHEET_ENGINE` | Auto-engine route for XLSX | `local` |
| `AUTO_HTML_ENGINE` | Auto-engine route for HTML and HTM | `html_local` |
| `AUTO_IMAGE_ENGINE` | Auto-engine route for PNG, JPG, and JPEG | `local` |
| `AUTO_TEXT_ENGINE` | Auto-engine route for TXT and MD | `local` |
| `OPENDATALOADER_HYBRID` | Optional hybrid backend for complex PDF pages | unset |
| `OPENDATALOADER_USE_STRUCT_TREE` | Enable structure-tree aware extraction for tagged PDFs | `false` |
| `FORMULA_OCR_ENABLED` | Run an optional postprocessor that replaces residual formula images with Markdown math | `false` |
| `FORMULA_OCR_PROVIDER` | Vision OCR backend for formula-image replacement (`mistral` or `deepseekocr`) | `mistral` |

### Engine dependency notes

| Engine | Install note | Notes |
| --- | --- | --- |
| `local` | Included in the base install | Internal extraction pipeline for PDF, DOCX, images, text, PPTX, and XLSX |
| `html_local` | `pip install ".[html]"` for best extraction quality | Installs `trafilatura` plus BeautifulSoup support, then falls back to regex stripping when needed |
| `mistral` | Base install plus `MISTRAL_API_KEY` | Remote OCR API; page headers and standalone page-number lines are omitted by default |
| `deepseekocr` | Base install plus `SILICONFLOW_API_KEY` | Remote OCR API via SiliconFlow |
| `markitdown` | `pip install ".[markitdown]"` | Microsoft MarkItDown-based conversion |
| `docling` | `pip install ".[docling]"` | Heavy transformer stack |
| `paddleocr` | `pip install ".[paddleocr]"` | GPU-friendly OCR path |
| `mineru` | `pip install ".[mineru]"` | GPU strongly recommended |
| `marker` | `pip install ".[marker]"` | GPU strongly recommended |
| `opendataloader` | `pip install ".[opendataloader]"` | PDF-only, requires Java 11+ on `PATH` |
| `api` | `pip install ".[api]"` | FastAPI plus uvicorn |
| `office` support | `pip install ".[office]"` | Installs PPTX and XLSX helpers |

### Formula-image postprocessing

Some PDF engines still leave formulas, matrix headers, or short mathematical labels as image references inside the Markdown.  
If you want those converted into Markdown math after the main document conversion step, enable the optional formula OCR pass:

```bash
# Windows PowerShell
$env:FORMULA_OCR_ENABLED="true"
$env:FORMULA_OCR_PROVIDER="mistral"
python -m doc_to_md.cli convert --input-path data/input --output-path data/output --engine opendataloader

# Unix/macOS
FORMULA_OCR_ENABLED=true FORMULA_OCR_PROVIDER=mistral \
python -m doc_to_md.cli convert --input-path data/input --output-path data/output --engine opendataloader
```

Current recommendation:

- Use `mistral` first for formula-heavy regulatory PDFs.
- Use `deepseekocr` only as a secondary option when you specifically want that OCR path.
- Leave the feature off for image-heavy documents where embedded figures should stay as images.

Math postprocessing also normalizes spacing around `_` and `^` inside math segments so Markdown renderers are less likely to misread subscripts or superscripts as italics.

## CLI usage

Install the package first with `pip install -e .`.

### Convert documents

```bash
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output \
  --engine local
```

Common flags:

- `--engine` / `--model`
- `--since 2025-05-01T00:00:00`
- `--dry-run`
- `--no-page-info`

### Auto engine

```bash
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output \
  --engine auto
```

Example routing:

```bash
DEFAULT_ENGINE=auto
AUTO_PDF_ENGINE=opendataloader
AUTO_HTML_ENGINE=html_local
AUTO_DOCX_ENGINE=markitdown
AUTO_PPTX_ENGINE=local
AUTO_SPREADSHEET_ENGINE=local
AUTO_IMAGE_ENGINE=local
AUTO_TEXT_ENGINE=local
```

### List engines

```bash
python -m doc_to_md.cli list-engines
# Output: local, mistral, deepseekocr, markitdown, paddleocr, mineru, docling, marker, html_local, auto, opendataloader
```

### Use the OpenDataLoader engine

Complete the install steps in [OpenDataLoader setup](#opendataloader-setup) first.

Examples:

```bash
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output \
  --engine opendataloader
```

Hybrid mode for harder tables or scanned pages:

```bash
# Windows PowerShell
$env:OPENDATALOADER_HYBRID="docling-fast"
python -m doc_to_md.cli convert --input-path data/input --output-path data/output --engine opendataloader

# Unix/macOS
OPENDATALOADER_HYBRID=docling-fast \
python -m doc_to_md.cli convert --input-path data/input --output-path data/output --engine opendataloader
```

## API usage

Install the API extra first:

```bash
pip install ".[api]"
```

Start the server:

```bash
doc-to-md-api
# or
uvicorn doc_to_md.api:app --reload
```

Available endpoints:

- `GET /health`
- `GET /apps/conversion/health`
- `GET /apps/conversion/engines`
- `POST /apps/conversion/convert`

Example request:

```bash
curl -X POST http://localhost:8000/apps/conversion/convert \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/input",
    "output_path": "data/output",
    "engine": "mistral",
    "no_page_info": true
  }'
```

## Supported formats and validation

- Supported file types: `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.html`, `.htm`, `.png`, `.jpg`, `.jpeg`, `.txt`, `.md`
- Legacy `.doc` is rejected explicitly
- Files must be non-empty and readable
- The validation layer rejects files larger than 100 MB

## Engines

- `local`: lightweight internal extraction pipeline
- `mistral`: Mistral OCR API, with optional PDF chunking and page-aware output
- `deepseekocr`: DeepSeek OCR via SiliconFlow
- `markitdown`: Microsoft MarkItDown-based local conversion
- `paddleocr`: local PaddleOCR pipeline for PDFs and images
- `mineru`: MinerU pipeline wrapper
- `docling`: IBM Docling pipeline wrapper
- `marker`: Marker PDF integration
- `html_local`: main-content HTML extraction with `trafilatura` fallback logic
- `auto`: format-aware dispatcher configured from settings
- `opendataloader`: Java-backed PDF conversion via `opendataloader-pdf`

All engines implement `Engine.convert(Path) -> EngineResponse`.

## Recommended PDF engines

Detailed scoring, install-cost analysis, dependency conflicts, and full benchmark coverage live in [PDF_ENGINE_EVALUATION.md](PDF_ENGINE_EVALUATION.md).

Final score weights are `25%` install cost, `25%` speed, and `50%` quality.

| Engine | Stars | Final score | Best for | Main tradeoff |
| --- | --- | ---: | --- | --- |
| `mistral` | `★★★★☆` | `3.9/5` | Best managed-service OCR result | Paid API and network dependency |
| `opendataloader` | `★★★★☆` | `3.8/5` | Best current local default for PDFs | Needs Java 11+ and can extract many images |
| `docling` | `★★★☆☆` | `2.9/5` | Best text fidelity on this sample | Too slow on CPU for default use |
| `markitdown` | `★★★☆☆` | `3.2/5` | Easiest local extra to try | Quality ceiling is limited |
| `local` | `★★★☆☆` | `3.2/5` | Fastest zero-extra baseline | Not good enough for quality-sensitive PDF work |
| `marker` | `★★★☆☆` | `2.7/5` | Rich Markdown plus many assets | Very slow and not practical in the main env |
| `mineru` | `★★☆☆☆` | `2.1/5` | Isolation-only benchmark coverage | Highest setup friction for limited payoff |
| `paddleocr` | `★☆☆☆☆` | `1.3/5` | Benchmark completeness only | Near-empty output on this sample |

Short reading of the table:

- `opendataloader` is the best local recommendation if Java is acceptable.
- `mistral` is the best result if a hosted OCR API is acceptable.
- `docling` is strongest on text quality, but too slow to be the default.
- `markitdown` is still the easiest local extra to recommend first.

Current sample artifacts:

- [`benchmark_results/ait170_ai_bulletin_january_2026_sample/report.md`](benchmark_results/ait170_ai_bulletin_january_2026_sample/report.md)
- [`benchmark_results/ait170_ai_bulletin_january_2026_sample/result.json`](benchmark_results/ait170_ai_bulletin_january_2026_sample/result.json)
- [`benchmark_results/ait170_ai_bulletin_january_2026_sample/outputs/`](benchmark_results/ait170_ai_bulletin_january_2026_sample/outputs/)

## Benchmarking

The repository includes `benchmark.py` for comparing engines on representative documents. Usage and examples are documented in [README_BENCHMARK.md](README_BENCHMARK.md). For recommendation logic and install-cost analysis, see [PDF_ENGINE_EVALUATION.md](PDF_ENGINE_EVALUATION.md).

Quick examples:

```bash
python benchmark.py --test-file path/to/document.pdf
python benchmark.py --test-file path/to/document.pdf --engines docling opendataloader mistral
python benchmark.py --test-file path/to/document.pdf --save-json
```

## Troubleshooting

- If `python -m doc_to_md.cli ...` fails with `ModuleNotFoundError`, install the package first with `pip install -e .`.
- If installation fails on Python 3.13 or 3.14, switch to Python 3.10, 3.11, or 3.12.
- If a remote engine fails to initialize, make sure the matching API key is set.
- If an optional engine import fails, install the matching extra or package for that engine.
- If `opendataloader` fails before conversion starts, verify `java -version` returns Java 11 or newer.
- If remote OCR times out, tune the `*_TIMEOUT_SECONDS`, `*_RETRY_ATTEMPTS`, and chunk or token settings in `.env`.

## Development and release checks

For full local test and release checks, install `requirements-dev.txt` after your chosen runtime environment.

Typical local checks:

```bash
python -m ruff check src tests config benchmark.py
python -m pytest -q
python -m build
python -m twine check dist/*
pip install -e .
```

The repository also includes GitHub Actions CI for `ruff`, `pytest`, `build`, and `twine check` across Python 3.10 to 3.12.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
