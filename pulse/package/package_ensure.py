from .install._install import PackageInstaller
import click

@click.command
def ensure():
    '''Ensures all packages are present.'''
    pckge = PackageInstaller()
    pckge.ensure_all_packages()