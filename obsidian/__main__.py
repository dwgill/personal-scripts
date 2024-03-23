import typer
from pathlib import Path
from .tags import tags_app

app = typer.Typer()
app.add_typer(tags_app, name="tag")

if __name__ == "__main__":
    app()