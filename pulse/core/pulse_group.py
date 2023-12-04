import click
from pulse.init.init import init
from .configure import configure

@click.group()
def pulse():
    """Pulse - Your open.mp package manager and build tools."""
    pass

pulse.add_command(init)
pulse.add_command(configure)