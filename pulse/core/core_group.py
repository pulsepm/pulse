import click

# from pulse.run.run import run
from pulse.config.config_configure import configure
from pulse.init.init import init
from pulse.pods.pods import pods
from pulse.install.install import install


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
pulse.add_command(install)