import click
from pulse.init.init import init
#from pulse.run.run import run
from pulse.config.config_configure import configure
from pulse.get.get import get

@click.group()
def pulse():
    """Pulse - Your open.mp package manager and build tools."""
    pass

pulse.add_command(init)
pulse.add_command(configure)
pulse.add_command(get)