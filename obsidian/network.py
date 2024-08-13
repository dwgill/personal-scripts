from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, Optional, Sequence
import typer
from util.markdown import get_front_matter_in_markdown_file, walk_md_with_tags
from util.validators import validate_directory
import util.airtable as airtable
from pydantic import BaseModel, ConfigDict, Field
import datetime as dt
import util.env



network_app = typer.Typer()


@network_app.command()
def airtable_sync(
    *,
    directory: Annotated[
        Path,
        typer.Option(
            ...,
            callback=validate_directory,
            help="Path to the vault to search for #Person notes.",
        ),
    ],
):
    """
    Sync all #Person notes in the given vault to corresponding
    records in the "Daniel Network" Airtable base.
    """

    people_to_upsert: dict[str, dict[str, Any]] = {}

    for fpath, tags in walk_md_with_tags(
        directory, predicate=lambda tags: "Person" in tags
    ):
        name = fpath.name.removesuffix(".md")
        frontmatter = get_front_matter_in_markdown_file(fpath)

        airtable_fields: dict[str, Any] = {
            "Name": name,
        }
        for field_def in network_field_definitions:
            if field_def.obsidian_frontmatter_field_name in frontmatter:
                frontmatter_value = frontmatter[field_def.obsidian_frontmatter_field_name]
                if frontmatter_value is None and not field_def.should_sync_empty_values:
                    continue
                airtable_fields[field_def.airtable_column_name] = frontmatter[
                    field_def.obsidian_frontmatter_field_name
                ]



        people_to_upsert[name] = airtable_fields

    airtable_api = airtable.AirtableApi()

    table = airtable_api.api.table(
        util.env.airtable_daniel_network_people_table_id(),
        util.env.airtable_daniel_network_people_table_id(),
    )

    table.batch_upsert(people_to_upsert.values(), ["Name"])

@dataclass
class NetworkFieldDefinition:
    obsidian_frontmatter_field_name: str
    airtable_column_name: str
    should_sync_empty_values: bool = field(default=False)


network_field_definitions: Sequence[NetworkFieldDefinition] = [
    NetworkFieldDefinition("birth date", "Birth Date", True),
    NetworkFieldDefinition("phone number", "Phone Number", True),
]



