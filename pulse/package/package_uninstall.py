import click
from .uninstall._uninstall import PackageUninstaller


@click.command
@click.argument("package", required=False, type=str)
@click.option(
    "--deep", "-d", required=False, is_flag=True, help="Deletes a package's cache."
)
def uninstall(package, deep):
    pcku = PackageUninstaller()
    pcku.delete(package, deep)
