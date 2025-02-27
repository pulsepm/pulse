import click

from pulse.init.init import init
from pulse.pods.pods import pods
from pulse.build.build import build
from pulse.run.run import run
from pulse.stroke.stroke import stroke
from pulse.package.package_pack import package
from pulse.release.release import release
from pulse.package.package_install import install
from pulse.package.package_ensure import ensure
from pulse.package.package_uninstall import uninstall
from pulse.user import user
import pulse.core.core_constants as core_constants

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(core_constants.PROJECT_VERSION)
    ctx.exit()


@click.group()
@click.option('-v', '--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help="Show the version and exit.")

def pulse() -> None:
    """Pulse - Your open.mp package manager and build tools.

    Returns:
        None
    """
    ...

pulse.add_command(init)
pulse.add_command(pods)
pulse.add_command(build)
pulse.add_command(run)
pulse.add_command(stroke)
pulse.add_command(package)
pulse.add_command(release)
pulse.add_command(install)
pulse.add_command(ensure)
pulse.add_command(uninstall)
pulse.add_command(user)