import os
import click
import pulse.core.config.config as config
from pulse.project.initialize import initialize, TYPE_GAMEMODE, TYPE_LIBRARY

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
    name = 'boiler'
    repo = 'boiler'
    project = 'boiler'
    default_name = 'NO_NAME_BRO'

    # check if .config exists and then load default_name.
    if config.exists():
        data = config.load()
        default_name = data['last_username']

    if library and gamemode:
        click.echo('Can\'t use both flags. Either initialize library or gamemode.')
    elif gamemode:
        name = click.prompt(f'Your name for publishing? Should be github username', default=default_name)
        if default_name == 'NO_NAME_BRO':
            click.echo('Fatal error: Input your name. Project hasn\'t been created.')

        name = default_name
            
        project = click.prompt('Enter the name for your gamemode project. It will be used as a project name')
        repo = click.prompt('Enter the name for your github repository. Could be left blank if you won\'t publish it')
        
        initialize(project, TYPE_GAMEMODE, name, repo)
    elif library:
        name = click.prompt('Your name for publishing?')
        project = click.prompt('Enter the name for your library project. It will be used as a project name')
        repo = click.prompt('Enter the name for your github repository. Could be left blank if you won\'t publish it')

        initialize(project, TYPE_LIBRARY, name, repo)
    else:
        click.echo('Invalid syntax. Use pulse --help')

# Znaci skines sa githuba release odabrane verzije
# Skines je gde je pokrenut init
# Deletujes qawno folder
# napravis gamemodes folder
# Napravis filterscripts folder