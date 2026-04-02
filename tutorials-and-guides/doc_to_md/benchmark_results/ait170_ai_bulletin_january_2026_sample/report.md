# Benchmark Report

## Sample

- Timestamp: `2026-03-24T07:58:09.998682+00:00`
- Test file: `data\input\ait170-ai-bulletin-january-2026_1.pdf`
- File size: 701.16 KB
- Engines tested: 8

## Summary

- Fastest successful engine: `local` at 3.40s.
- Longest Markdown output: `marker` with 124,355 characters.

## Successful engines ranked by runtime

1. `local` - 3.40s, 115,965 chars, 0 assets
2. `markitdown` - 20.44s, 113,587 chars, 0 assets
3. `opendataloader` - 21.19s, 112,618 chars, 60 assets
4. `mistral` - 29.19s, 110,549 chars, 14 assets
5. `paddleocr` - 179.20s, 1,385 chars, 0 assets
6. `docling` - 276.35s, 114,482 chars, 0 assets
7. `mineru` - 1935.67s, 103,466 chars, 11 assets
8. `marker` - 5990.15s, 124,355 chars, 59 assets

## Result table

| Engine | Model | Status | Time | Markdown chars | Assets | Artifact |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `local` | `local-text-wrapper` | success | 3.40s | 115,965 | 0 | `outputs\local\output.md` |
| `markitdown` | `markitdown` | success | 20.44s | 113,587 | 0 | `outputs\markitdown\output.md` |
| `paddleocr` | `paddleocr-en` | success | 179.20s | 1,385 | 0 | `outputs\paddleocr\output.md` |
| `docling` | `docling` | success | 276.35s | 114,482 | 0 | `outputs\docling\output.md` |
| `marker` | `marker` | success | 5990.15s | 124,355 | 59 | `outputs\marker\output.md` |
| `mineru` | `pipeline:auto` | success | 1935.67s | 103,466 | 11 | `outputs\mineru\output.md` |
| `mistral` | `mistral-ocr-latest` | success | 29.19s | 110,549 | 14 | `outputs\mistral\output.md` |
| `opendataloader` | `opendataloader` | success | 21.19s | 112,618 | 60 | `outputs\opendataloader\output.md` |

## Engine notes

### PaddleOCR (`paddleocr`)

- Best for: Cases where you specifically want Paddle's OCR stack and are willing to manage the runtime.
- Pros:
  - Can use a local GPU-backed OCR stack when Paddle is configured correctly.
  - Works without an external OCR API.
  - Useful when you want a pure OCR-oriented path instead of a full layout pipeline.
- Cons:
  - Runtime setup is heavier than the Python extra alone suggests.
  - Windows GPU runs may require explicit CUDA DLL paths for the bundled Paddle runtime.
  - This sample produced very little usable text despite a successful run.
- Measured on this sample: 179.20s, 1,385 Markdown chars, 0 assets.

### Docling (`docling`)

- Best for: Complex PDFs where local structured extraction matters more than raw speed.
- Pros:
  - Strong document structure recovery on complex PDFs.
  - Good fit for enterprise reports and long-form documents.
  - Runs locally once dependencies are installed.
- Cons:
  - Heavy dependency stack and slower startup.
  - Runtime is usually much higher than API OCR on the same sample.
  - Environment setup is less lightweight than core engines.
- Measured on this sample: 276.35s, 114,482 Markdown chars, 0 assets.

### Marker (`marker`)

- Best for: One-off or high-fidelity local conversions where heavy setup and long runtime are acceptable.
- Pros:
  - Produced the longest Markdown output in this benchmark.
  - Recovered rich structure and extracted many page assets.
  - Can be very strong when quality matters more than install simplicity.
- Cons:
  - Requires an isolated environment in this project because of dependency conflicts.
  - Runtime on this sample was extremely high.
  - Still shows OCR and punctuation artifacts in the output.
- Measured on this sample: 5990.15s, 124,355 Markdown chars, 59 assets.

### MinerU (`mineru`)

- Best for: Research or specialized evaluation work where you explicitly want to test MinerU despite its setup overhead.
- Pros:
  - Recovered a usable long-form Markdown document after isolated-environment setup.
  - Includes its own layout and OCR pipeline rather than relying on a remote API.
  - Extracted a smaller, more restrained asset set than some other local engines.
- Cons:
  - Needed the most manual runtime repair to get working in this repository.
  - Runtime was still very high on this sample.
  - Output quality did not justify the setup cost compared with the better local alternatives.
- Measured on this sample: 1935.67s, 103,466 Markdown chars, 11 assets.

### Mistral OCR (`mistral`)

- Best for: Production OCR when quality and convenience matter more than avoiding API usage.
- Pros:
  - Usually the easiest way to get high-quality OCR on difficult PDFs.
  - No local OCR model installation required.
  - Often the best speed-to-quality tradeoff when the API is available.
- Cons:
  - Requires a working API key and outbound network access.
  - Usage is not free.
  - Remote latency and service availability affect runtime.
- Measured on this sample: 29.19s, 110,549 Markdown chars, 14 assets.

### OpenDataLoader (`opendataloader`)

- Best for: PDF-heavy workflows where you can maintain the Java runtime and optional package.
- Pros:
  - Purpose-built PDF pipeline with Java-backed layout analysis.
  - Supports hybrid mode for harder pages.
  - Can be a strong local option once prerequisites are satisfied.
- Cons:
  - Requires both Java 11+ and the optional Python package.
  - Current environment readiness is a hard prerequisite.
  - PDF-only, so it is not a general document engine.
- Measured on this sample: 21.19s, 112,618 Markdown chars, 60 assets.
