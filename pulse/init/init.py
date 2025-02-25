import click

from ..user import User
from pulse.git.git import create_repository
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
    
    usr = User()
    
    name = click.prompt(
        "Your GitHub username",
        default=usr.git_user,
    )

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

    if create:
        create_repository(name, repo, usr.git_token)
