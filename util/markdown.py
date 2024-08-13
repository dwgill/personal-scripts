import frontmatter
import obsidiantools
from pathlib import Path
from typing import Any, Callable, Iterable, Literal, NamedTuple


def walk_md(
    directory: Path, *, on_skip_non_md: Callable[[Path], Any] | None = None
) -> Iterable[Path]:
    if not directory.is_dir():
        raise ValueError("directory parameter must be a directory.")

    for root, _dirs, files in directory.walk():
        for file in (root / f for f in files):
            if file.suffix != ".md":
                if on_skip_non_md is not None:
                    on_skip_non_md(file)

                continue

            yield file


def walk_md_with_tags(
    directory: Path,
    predicate: Callable[[set[str]], bool] | None = None,
) -> Iterable["WalkMdWithTagsResult"]:
    if predicate is None:
        predicate = lambda tags: True

    for fpath in walk_md(directory):
        tags = get_tags_in_markdown_file(fpath)
        if predicate(tags):
            yield WalkMdWithTagsResult(file=fpath, tags=tags)


class WalkMdWithTagsResult(NamedTuple):
    file: Path
    tags: set[str]


def get_tags_in_markdown_file(
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


def get_front_matter_in_markdown_file(
    file: Path,
) -> dict[str, Any]:
    if not file.is_file():
        raise ValueError("file parameter must be file.")
    if file.suffix != ".md":
        raise ValueError("file parameter must be a markdown file.")

    with file.open(encoding="utf-8-sig") as ffile:
        post = frontmatter.load(ffile)
        return dict(post.metadata)

