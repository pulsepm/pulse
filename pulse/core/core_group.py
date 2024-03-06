import click
from pulse.init.init import init
# from pulse.run.run import run
from pulse.config.config_configure import configure
from pulse.pods.pods import pods


@click.group()
def pulse() -> None:
    """Pulse - Your open.mp package manager and build tools.
    
    Returns:
        None
    """
    ...


pulse.add_command(init)
pulse.add_command(configure)
pulse.add_command(pods)
