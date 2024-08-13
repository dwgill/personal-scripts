from typing import Annotated, Iterable, Literal
import typer
from pathlib import Path
import frontmatter

from util.markdown import get_tags_in_markdown_file, walk_md
from util.validators import validate_directory, validate_tag

tags_app = typer.Typer()


@tags_app.command()
def apply(
    *,
    directory: Annotated[
        Path,
        typer.Option(
            ...,
            callback=validate_directory,
            help="Path to the directory of notes to apply the tag to.",
        ),
    ],
    tag: Annotated[
        str,
        typer.Option(
            ...,
            callback=validate_tag,
            help="Tag to apply to all notes in the directory.",
        ),
    ],
):
    """
    Update all notes in the specified directory to have the given
    tag.
    """

    for fpath in walk_md(
        directory,
        on_skip_non_md=lambda f: typer.echo(f"Skipped (non-markdown file): {f}"),
    ):
        file_tags = get_tags_in_markdown_file(fpath)
        if tag in file_tags:
            typer.echo(f"Skipped (tag already present): {fpath}")
            continue

        file_tags_lc = {t.lower() for t in file_tags}
        if tag.lower() in file_tags_lc:
            typer.echo(f"Skipped (tag already present): {fpath}")
            continue

        add_tag_to_file(fpath, tag, existing_tags=file_tags)
        typer.echo(f"Added tag: {fpath}")


def add_tag_to_file(
    file: Path, tag: str, *, existing_tags: Iterable[str] | None = None
):
    if existing_tags is None:
        existing_tags = get_tags_in_markdown_file(file)

    new_tags = set(existing_tags)

    if tag in new_tags:
        return

    new_tags.add(tag)

    with file.open(mode="r", encoding="utf-8-sig") as ffile:
        post = frontmatter.load(ffile)

    post.metadata["tags"] = list(new_tags)

    new_file_text = frontmatter.dumps(post)

    with file.open(mode="w", encoding="utf-8-sig") as ffile:
        ffile.write(new_file_text)
