"""Typer CLI for the conversion app."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional

import typer

from doc_to_md.apps.conversion.logic import list_engine_names, run_conversion
from doc_to_md.utils.logging import log_info

app = typer.Typer(help="Convert documentation sources into Markdown using pluggable engines.")


@app.command()
def convert(
    input_path: Annotated[Optional[str], typer.Option("--input-path", help="Directory of input docs; defaults to settings.input_dir")] = None,
    output_path: Annotated[Optional[str], typer.Option("--output-path", help="Where to write Markdown files")] = None,
    engine: Annotated[Optional[str], typer.Option("--engine", "-e", help="Engine name override")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="Model override for engines that support it")] = None,
    since: Annotated[
        Optional[datetime],
        typer.Option(
            "--since",
            help="Process only files modified on/after this timestamp (ISO 8601, e.g. 2025-05-01T00:00:00).",
        ),
    ] = None,
    no_page_info: Annotated[bool, typer.Option("--no-page-info", help="Omit page headers and strip page footers from output")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="List eligible files without converting or writing output")] = False,
) -> None:
    try:
        run_conversion(
            input_path=input_path,
            output_path=output_path,
            engine=engine,
            model=model,
            since=since,
            no_page_info=no_page_info,
            dry_run=dry_run,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - bubble Typer-friendly errors
        raise typer.Exit(code=1) from exc


@app.command()
def list_engines() -> None:
    """Pretty-print available engines."""
    for name in list_engine_names():
        log_info(name)
