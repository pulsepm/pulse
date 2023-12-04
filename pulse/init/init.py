import os
import click 
from pulse.project.initialize import Project, TYPE_GAMEMODE, TYPE_LIBRARY

@click.command
@click.option('-g', '--gamemode', is_flag=True, help='Initialize a game mode package')
@click.option('-l', '--library', is_flag=True, help='Initialize a library package')
def init(gamemode: bool, library: bool) -> None:
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
    if library and gamemode:
        click.echo('Can\'t use both flags. Either initialize library or gamemode.')
    elif gamemode:
        gamemode = Project('boiler', TYPE_GAMEMODE, 'Mergevos', 'boiler')
    elif library:
        gamemode = Project('boiler', TYPE_LIBRARY, 'Mergevos', 'boiler')
    else:
        click.echo('Invalid syntax. Use pulse --help')

