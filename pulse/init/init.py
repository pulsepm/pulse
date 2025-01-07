import click

import pulse.config.config as config
from pulse.core.git.git import create_repository
from pulse.project.initialize import initialize


@click.command
@click.option('--local', '-l', is_flag=True, default=False, help="Initialize package locally.")
def init(local: bool) -> None:
    """
    Initialize a new Pulse project.

    Returns:
        None
    """
    name = "boiler"
    repo = "boiler"
    project = "boiler"
    default_name = "NO_NAME_BRO"
    data = {}

    # check if .config exists and then load default_name.
    if config.exists():
        data = config.load()
        default_name = data["last_username"]

    name = click.prompt(
        "Your GitHub username",
        default=default_name if default_name != "NO_NAME_BRO" else None,
    )
    data["last_username"] = name

    project = click.prompt(
        "Project name"
    )
    repo = click.prompt(
        "Repository name",
        default=project,
    )
    entry = click.prompt("Name of your entry file", default="main.pwn")
    create = click.confirm("Initialize git repository?", default=False)
    pods = click.confirm(
        "Isolate the project - Pulse Pods? You can always do it later", default=False
    )

    output = str(entry).replace(".pwn", ".amx")
    initialize(project, name, repo, pods, local, entry, output)
    config.write(data, "wb")

    if create:
        create_repository(name, repo, data["token"])
