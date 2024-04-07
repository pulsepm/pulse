import click

import pulse.config.config as config
from pulse.core.git.git import create_repository
from pulse.project.initialize import initialize


@click.command
def init() -> None:
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
        "Your name for publishing? Should be github username",
        default=default_name if default_name != "NO_NAME_BRO" else None,
    )
    data["last_username"] = name

    project = click.prompt(
        "Enter the name for your project. It will be used as a project name"
    )
    repo = click.prompt("Enter the name for your github repository.")
    entry = click.prompt("Input the name of your entry file", default="main.pwn")
    create = click.confirm("Initialize the repo?", default=False)
    pods = click.confirm(
        "Isolate the project - Pulse Pods? You can always do it later", default=False
    )

    output = str(entry).replace(".pwn", ".amx")
    initialize(project, name, repo, pods, entry, output)
    config.write(data, "wb")

    if create:
        click.secho("Repository has been created successfully", fg="green")
        create_repository(name, repo, data["token"])
