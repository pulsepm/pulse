import os
import click
import pulse.config.config as config
from pulse.core.git.git import create_repository
from pulse.project.initialize import initialize

@click.command
def init() -> None:
    """
    Initialize a new Pulse project.

    Args:
        gamemode (bool): If True, initialize a game mode package.
        library (bool): If True, initialize a library package.

    Returns:
        None

    Usage:
        pulse init -g  # Initialize a game mode package (or --gamemode)
        pulse init -l  # Initialize a library package (or --library)

    Raises:
        click.exceptions.UsageError: If both -g (--gamemode) and -l (--library) flags are used simultaneously.
    """
    name = 'boiler'
    repo = 'boiler'
    project = 'boiler'
    default_name = 'NO_NAME_BRO'
    data = None

    # check if .config exists and then load default_name.
    if config.exists():
        data = config.load()
        default_name = data['last_username']

    name = click.prompt(f'Your name for publishing? Should be github username', default=default_name if default_name != 'NO_NAME_BRO' else None)
    data['last_username'] = name

    project = click.prompt('Enter the name for your project. It will be used as a project name')
    repo = click.prompt('Enter the name for your github repository.')
    create = click.confirm('Initialize the repo?', default=True)

    initialize(project, name, repo)
    config.write(data, 'w')

    if create:
        click.secho('Repository has been created successfully', fg='green')
        create_repository(name, repo, data['token'])