# PDF Engine Evaluation Report

## Why this document exists

`README.md` should stay short and decision-oriented. This report keeps the detailed PDF engine evaluation in one place: install cost, package weight, dependency conflicts, benchmark results, and the scoring method behind the recommendations.

## Scope

- Sample document: `data/input/ait170-ai-bulletin-january-2026_1.pdf`
- Sample size: `717,988` bytes
- Current goal: recommend practical PDF engines for ordinary users, not just technically available ones
- Included engine inventory: `local`, `markitdown`, `opendataloader`, `docling`, `paddleocr`, `marker`, `mineru`, `mistral`, `deepseekocr`
- Excluded from this report: `auto` because it is a router, not a standalone extractor; `html_local` because it is not a PDF path
- Full benchmark coverage completed in this report: `local`, `markitdown`, `opendataloader`, `docling`, `paddleocr`, `marker`, `mineru`, `mistral`
- Still intentionally excluded from recommendation work: `deepseekocr`, because it is another third-party remote OCR path the project owner does not want to prioritize

Current sample artifacts:

- Benchmark summary: [`benchmark_results/ait170_ai_bulletin_january_2026_sample/report.md`](benchmark_results/ait170_ai_bulletin_january_2026_sample/report.md)
- Raw machine-readable results: [`benchmark_results/ait170_ai_bulletin_january_2026_sample/result.json`](benchmark_results/ait170_ai_bulletin_january_2026_sample/result.json)
- Per-engine outputs: [`benchmark_results/ait170_ai_bulletin_january_2026_sample/outputs/`](benchmark_results/ait170_ai_bulletin_january_2026_sample/outputs/)

## Evaluation method

### 1. Install cost

Install cost is scored from `5` down to `1`.

- `5`: base install or very small extra, no system dependency, no resolver conflict
- `4`: moderate extra, no serious system dependency, low friction
- `3`: extra plus one meaningful prerequisite such as Java, or a service/API dependency
- `2`: heavy stack with large dependency payload or likely runtime model downloads
- `1`: conflicts with current project pins, or heavy enough that an isolated environment is the honest recommendation

Install cost is judged from:

- clean-environment package count
- approximate download payload
- system prerequisites such as Java or GPU-oriented stacks
- compatibility with the current project pins
- external service requirements such as API keys and network access
- extra runtime repair work that was actually needed to get a successful run

Method note:

- Package count and payload were measured with `pip install --dry-run --ignore-installed --report ...`
- Approximate payload is the sum of resolver download URLs' `Content-Length`
- Payload does not include Java, CUDA, unpacked wheel size, pip cache growth, or lazy model downloads after first run
- When a benchmark required substantial runtime additions beyond the extra itself, that cost is called out separately

### 2. Speed

Speed is measured on the same machine, using the same PDF, with a single conversion per engine.

- `5`: under `5s`
- `4`: `5s` to `30s`
- `3`: `30s` to `90s`
- `2`: `90s` to `180s`
- `1`: over `180s`

### 3. Quality

Quality is the most important axis for PDF workflows. The score is sample-specific and combines heuristic signals with manual review.

Quality weights:

- Structure fidelity: `35%`
- Text cleanliness: `35%`
- Content completeness: `20%`
- Asset usefulness: `10%`

Heuristics tracked for each output:

- heading count
- table row count
- image reference count
- bullet count
- page marker count
- suspicious token count for recurring mojibake markers, copyright artifacts, replacement characters, and form-feed

The heuristic layer is only a guide. Final quality scores also reflect manual spot checks of the opening pages, table of contents, section headings, and mid-document body text.

### 4. Final weighted score and star view

Final score is a weighted average of the three main axes:

- Install cost: `25%`
- Speed: `25%`
- Quality: `50%`

Formula:

`final_score = install_cost * 0.25 + speed * 0.25 + quality * 0.50`

Star view is just a compact display of the final score:

- `4.5` to `5.0`: `★★★★★`
- `3.5` to `4.4`: `★★★★☆`
- `2.5` to `3.4`: `★★★☆☆`
- `1.5` to `2.4`: `★★☆☆☆`
- below `1.5`: `★☆☆☆☆`

This sample is scored strictly, so no engine lands at `★★★★★`. That is expected, not a bug in the table.

## Engine inventory and install cost

| Engine | What must be installed | Clean-env package count | Approx payload | Current project installability | Current benchmark status | Notes |
| --- | --- | ---: | ---: | --- | --- | --- |
| `local` | Base install only | `0` extra | `0` extra | Works now | Benchmarked | Fastest possible baseline, but weak PDF quality on this sample |
| `markitdown` | `pip install -e ".[markitdown]"` | `33` | `63.0 MiB` | Works now | Benchmarked | Simplest local extra after base install |
| `opendataloader` | Java `11+` and `pip install -e ".[opendataloader]"` | `1` Python package | `21.2 MiB` plus Java | Works now after Java setup | Benchmarked | Small Python payload, but Java is a real setup step |
| `docling` | `pip install -e ".[docling]"` | `95` | `293.3 MiB` | Works now | Benchmarked | Heavy dependency stack, CPU-slow on this sample |
| `paddleocr` | `pip install -e ".[paddleocr]"`, plus a working Paddle runtime | `58` extra-only | `99.1 MiB` extra-only; about `1.9 GB` more for the working Windows GPU runtime used here | Works in the main env only after extra runtime setup | Benchmarked | Successful run required `paddlepaddle-gpu==3.3.0` and explicit CUDA DLL paths on Windows |
| `marker` | `pip install -e ".[marker]"` in an isolated env | `78` | `250.4 MiB` | Fails in the main env | Benchmarked in an isolated env | Very strong output, but not honest to present as a drop-in extra in this repo |
| `mineru` | `pip install -e ".[mineru]"` in an isolated env, plus runtime repair | `82` | `214.0 MiB` | Fails in the main env | Benchmarked in an isolated env | Needed the most manual runtime repair before the benchmark would succeed |
| `mistral` | Base install plus `MISTRAL_API_KEY` | `0` extra | `0` extra | Works now | Benchmarked | Paid remote service; install is easy but operationally external |
| `deepseekocr` | Base install plus `SILICONFLOW_API_KEY` | `0` extra | `0` extra | Works now | Intentionally skipped | Supported, but excluded from recommendation work because it is another third-party remote OCR path |

### Recommended minimal retained setup

If the project keeps only the currently recommended PDF engines:

- `local`
- `markitdown`
- `opendataloader`
- `docling`
- `mistral`

the official install target is:

```bash
pip install -r requirements-recommended-pdf.txt
```

Equivalent direct command:

```bash
pip install -e ".[markitdown,docling,opendataloader]"
```

Why this is enough:

- `local` is part of the base package
- `mistral` is part of the base package and only needs `MISTRAL_API_KEY`
- `markitdown`, `docling`, and `opendataloader` are the only extras needed for that retained set
- `requirements-core.txt` is broader than this retained set and should not be presented as the same thing

### Observed installed footprint for the retained setup

The `Approx payload` column above is a download estimate. Actual installed size is larger.

On the Windows / Python 3.12 machine used for this evaluation, after removing the heavier engines and rebuilding only the retained set:

- `.venv`: about `1.32 GB`
- JDK required by `opendataloader`: about `303 MB`
- practical total: about `1.62 GB`

Largest installed components in that retained setup:

- `torch`: about `447 MB`
- `scipy`: about `111 MB`
- `cv2`: about `109 MB`
- `transformers`: about `102 MB`
- `sympy`: about `66 MB`
- `pandas`: about `60 MB`
- `onnxruntime`: about `35 MB`
- `docling_parse`: about `29 MB`
- `opendataloader_pdf`: about `23 MB`

Interpretation:

- most of the retained footprint comes from the `docling` stack, not from `markitdown` or `opendataloader` alone
- `opendataloader` itself is relatively small on the Python side, but its Java requirement adds a separate system footprint
- the retained set is much smaller than the previous mixed local-plus-GPU environments, but it is still not a lightweight install in absolute terms

### Current dependency conflicts

These are real resolver conflicts in the current project, not guesses.

| Engine | Conflict |
| --- | --- |
| `marker` | Project pins `click==8.1.7`, while `marker-pdf>=1.10.1` requires `click>=8.2.0,<9` |
| `mineru` | Project pins `pillow==10.4.0`, while `mineru>=2.6.4` requires `pillow>=11.0.0` |

### Runtime repair that was actually needed

This matters because install cost is not just the first `pip install` line.

- `paddleocr`: the Python extra alone was not enough for a working Windows GPU run. A successful benchmark needed `paddlepaddle-gpu==3.3.0` from Paddle's `cu130` index and a process-level `PATH` update pointing at the bundled `nvidia/cu13` and `nvidia/cudnn` DLL directories.
- `marker`: the benchmark worked only in an isolated environment so it could use `click>=8.2.0` without touching the repository pins.
- `mineru`: the benchmark worked only after an isolated environment plus additional runtime packages and version adjustments, including `torch==2.2.2`, `torchvision==0.17.2`, `doclayout-yolo`, `ultralytics`, `ftfy`, `pyclipper`, `omegaconf`, `rapidocr`, `shapely`, `dill`, and `numpy<2`.

### Install-cost interpretation

- `markitdown` is still the easiest true extra to recommend right now.
- `opendataloader` remains the best "serious local PDF engine" from a setup-vs-output point of view.
- `paddleocr` looked moderate on paper, but the successful Windows GPU run was much heavier than the extra-only numbers suggest.
- `marker` and `mineru` are now benchmarked, but their installation cost is clearly product-level friction, not a documentation gap.

## Full benchmark results

| Engine | Time | Markdown chars | Assets | Install cost score | Speed score | Quality score | Final score | Stars | Working conclusion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `mistral` | `29.19s` | `110,549` | `14` | `3.5` | `4.0` | `4.0` | `3.88` | `★★★★☆` | Best managed-service option if API use is acceptable |
| `opendataloader` | `21.19s` | `112,618` | `60` | `3.5` | `4.0` | `3.8` | `3.77` | `★★★★☆` | Best current local balance |
| `local` | `3.40s` | `115,965` | `0` | `5.0` | `5.0` | `1.4` | `3.20` | `★★★☆☆` | Fast zero-extra baseline only |
| `markitdown` | `20.44s` | `113,587` | `0` | `4.0` | `4.0` | `2.3` | `3.15` | `★★★☆☆` | Best "just add one local extra" option |
| `docling` | `276.35s` | `114,482` | `0` | `2.0` | `1.0` | `4.3` | `2.90` | `★★★☆☆` | Best current text fidelity, but too slow for default CPU use |
| `marker` | `5990.15s` | `124,355` | `59` | `1.5` | `1.0` | `4.1` | `2.67` | `★★★☆☆` | Strong output, worst runtime and high setup cost |
| `mineru` | `1935.67s` | `103,466` | `11` | `1.0` | `1.0` | `3.2` | `2.10` | `★★☆☆☆` | Works after major setup effort, but not worth the cost here |
| `paddleocr` | `179.20s` | `1,385` | `0` | `1.5` | `2.0` | `0.8` | `1.27` | `★☆☆☆☆` | Runtime success, but near-empty output on this sample |

## Quality evidence

### Heuristic snapshot

| Engine | Headings | Table rows | Image refs | Bullets | Page markers | Suspicious tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `local` | `1` | `0` | `0` | `0` | `0` | `204` |
| `markitdown` | `0` | `0` | `0` | `0` | `0` | `243` |
| `opendataloader` | `119` | `19` | `21` | `169` | `0` | `204` |
| `docling` | `145` | `33` | `0` | `95` | `0` | `204` |
| `mistral` | `165` | `31` | `14` | `92` | `0` | `204` |
| `paddleocr` | `41` | `0` | `0` | `0` | `0` | `0` |
| `marker` | `147` | `33` | `59` | `111` | `0` | `228` |
| `mineru` | `120` | `0` | `2` | `0` | `0` | `200` |

Notes:

- Suspicious token count is only a rough signal. This sample repeats the same copyright and punctuation corruption many times, which inflates every engine that actually extracted text.
- `paddleocr` looks "clean" by the token count only because it mostly emitted `_No text detected._`, not because the extraction quality was strong.

### Manual quality notes

| Engine | Structure fidelity | Text cleanliness | Content completeness | Asset usefulness | Why it landed here |
| --- | ---: | ---: | ---: | ---: | --- |
| `local` | `1` | `1` | `3` | `1` | Fastest output, but obvious OCR noise, broken punctuation, weak Markdown structure, and poor readability for quality-sensitive PDF work |
| `markitdown` | `2` | `2` | `4` | `1` | Cleaner than `local`, but still mostly flattened text with weak hierarchy recovery and recurring mojibake |
| `opendataloader` | `4` | `3` | `4` | `5` | Strong heading recovery and rich asset extraction; still carries quote and encoding artifacts, and image extraction can be aggressive |
| `docling` | `5` | `4` | `5` | `1` | Best long-form structure and body-text reconstruction on this sample; loses points mainly on speed and lack of assets, not text quality |
| `mistral` | `4` | `4` | `4` | `4` | Very solid structure and good OCR quality; page markers and API dependency keep it from being the default local recommendation |
| `paddleocr` | `1` | `1` | `0` | `0` | Technically ran, but the sample output was mostly repeated `_No text detected._` page stubs, so quality is effectively unusable here |
| `marker` | `4` | `3` | `5` | `5` | Very rich Markdown plus many extracted assets; quality is strong, but not clean enough to justify the install and runtime burden for ordinary users |
| `mineru` | `4` | `2` | `4` | `3` | Recovered a usable document, but still showed visible punctuation and spacing artifacts and did not outperform the stronger local alternatives |

## What this means right now

### Best current local recommendation: `opendataloader`

Why:

- close to `markitdown` on runtime
- much better structure recovery than `markitdown`
- useful asset extraction
- realistic setup burden compared with `docling`, `marker`, and `mineru`

Tradeoffs:

- Java setup needs to be explained clearly
- extraction is image-heavy on this sample
- text is still not as clean as the best managed OCR output

### Best current local text quality: `docling`

Why:

- strongest table of contents and section recovery among the practical local options
- best long-form text readability in this sample

Tradeoff:

- `276.35s` is too slow to be the default recommendation for ordinary CPU workflows

### Highest-output local engine, but not a practical default: `marker`

Why:

- longest Markdown output in this benchmark
- rich structure and strong asset extraction

Tradeoffs:

- isolated environment required in this repository
- `5990.15s` runtime is far beyond normal default-engine tolerance
- output quality is strong, but not so much stronger that it justifies the setup and runtime cost for most users

### Best current lightweight local extra: `markitdown`

Why:

- straightforward install story
- moderate dependency weight
- materially better than `local` for PDF text cleanup

Tradeoff:

- quality ceiling is clearly lower than `opendataloader`, `docling`, `marker`, and `mistral`

### Best current managed-service option: `mistral`

Why:

- good quality without local heavy stack management
- much faster than `docling`, `mineru`, and `marker`

Tradeoffs:

- paid API
- network dependency
- not ideal if the recommendation should stay fully local or vendor-independent

### Not recommended on this sample: `paddleocr`

Why:

- the successful Windows GPU setup was much heavier than expected
- despite that setup, the output was mostly empty page stubs

Tradeoff:

- on this sample it combines high setup cost with poor extraction quality, which is the worst combination in the whole benchmark

### Works, but not worth the setup cost here: `mineru`

Why:

- full run succeeded after isolated-environment setup and runtime repair
- output is usable, not catastrophic

Tradeoff:

- the setup burden was the highest in this repository
- runtime was still over half an hour
- quality did not beat `opendataloader`, `docling`, or `mistral`

### Fastest baseline, but not a recommendation: `local`

Why:

- zero extra installation
- very fast

Tradeoff:

- quality is too weak for serious PDF-to-Markdown workflows unless the document is very clean or the output is only a rough draft

## Coverage status

### Completed in the main project environment

- `local`
- `markitdown`
- `opendataloader`
- `docling`
- `mistral`

### Completed only after extra runtime work

- `paddleocr`

### Completed only in isolated environments

- `marker`
- `mineru`

### Still intentionally out of scope

- `deepseekocr`

## Short conclusion for README

If README stays concise, the current summary should be:

- `opendataloader` is the best current local default for PDFs when Java is acceptable
- `mistral` is the best current managed-service OCR path
- `docling` has the best practical local text quality in this sample, but is too slow on CPU to be the default
- `markitdown` is the easiest local extra to try after base install
- `marker` and `mineru` are now benchmarked, but their install cost is too high to recommend as default paths
- `paddleocr` is now benchmarked too, and it underperformed badly on this sample
- `local` should be described as a fast baseline, not a quality recommendation
