import click

# from pulse.run.run import run
from pulse.config.config_configure import configure
from pulse.init.init import init
from pulse.pods.pods import pods
from pulse.install.install import install
from pulse.uninstall.uninstall import uninstall
from pulse.ensure.ensure import ensure


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
pulse.add_command(uninstall)
pulse.add_command(ensure)
