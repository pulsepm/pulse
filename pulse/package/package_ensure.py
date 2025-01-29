from .install._install import install_all_packages

import click

@click.command
def ensure():
    '''Ensures all packages are present.'''
    install_all_packages()