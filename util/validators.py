"""
Functions for use with the 'callback'
parameter of typer.Option and typer.Argument.
"""

from pathlib import Path
import typer


def validate_directory(value: Path):
    if not value.exists():
        raise typer.BadParameter("Directory does not exist.")
    if not value.is_dir():
        raise typer.BadParameter("Directory is not directory.")
    return value


def validate_tag(value: str):
    return value.strip().lstrip("#")
