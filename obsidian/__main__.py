import typer
from pathlib import Path
from .tags import tags_app
from .network import network_app

app = typer.Typer()
app.add_typer(tags_app, name="tag")
app.add_typer(network_app, name="network")

if __name__ == "__main__":
    app()