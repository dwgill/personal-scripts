from typing import Annotated, Iterable, Literal
import typer
from pathlib import Path
import obsidiantools
import frontmatter

tags_app = typer.Typer()


def validate_directory(value: Path):
    if not value.exists():
        raise typer.BadParameter("Directory does not exist.")
    if not value.is_dir():
        raise typer.BadParameter("Directory is not directory.")
    return value


def validate_tag(value: str):
    return value.strip().lstrip("#")


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

    for root, _dirs, files in directory.walk():
        for file in (root / f for f in files):
            if file.suffix != ".md":
                typer.echo(f"Skipped (non-markdown file): {file}")
                continue

            file_tags = get_tags_in_file(file)
            if tag in file_tags:
                typer.echo(f"Skipped (tag already present): {file}")
                continue

            file_tags_lc = {t.lower() for t in file_tags}
            if tag.lower() in file_tags_lc:
                typer.echo(f"Skipped (tag already present): {file}")
                continue

            add_tag_to_file(file, tag, existing_tags=file_tags)
            typer.echo(f"Added tag: {file}")

def add_tag_to_file(
    file: Path, tag: str, *, existing_tags: Iterable[str] | None = None
):
    if existing_tags is None:
        existing_tags = get_tags_in_file(file)

    new_tags = set(existing_tags)

    if tag in new_tags:
        return

    new_tags.add(tag)

    with file.open(mode='r', encoding="utf-8-sig") as ffile:
        post = frontmatter.load(ffile)

    post.metadata["tags"] = list(new_tags)

    new_file_text = frontmatter.dumps(post)

    with file.open(mode="w", encoding="utf-8-sig") as ffile:
        ffile.write(new_file_text)


def get_tags_in_file(
    file: Path, *, method: Literal["frontmatter", "obsidiantools"] = "frontmatter"
) -> set[str]:
    if not file.is_file():
        raise ValueError("file parameter must be file.")
    if file.suffix != ".md":
        raise ValueError("file parameter must be a markdown file.")

    tags_in_body = set(obsidiantools.md_utils.get_tags(file, show_nested=True))
    if method == "obsidiantools":
        front_matter = obsidiantools.md_utils.get_front_matter(file)
        front_matter_tags_raw = front_matter.get("tags")
    elif method == "frontmatter":
        with file.open(encoding="utf-8-sig") as ffile:
            post = frontmatter.load(ffile)
            front_matter_tags_raw = post.metadata.get("tags")

    if not isinstance(front_matter_tags_raw, list):
        front_matter_tags = set[str]()
    else:
        front_matter_tags = {t for t in front_matter_tags_raw if isinstance(t, str)}

    return tags_in_body | front_matter_tags
