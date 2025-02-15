import os
import click
import logging

from .install._install import PackageInstaller

'''
- user executes `pulse install user/repo`
- pulse checks if we are in a pulse project; if not: inform the user and exit;
- Check if such package exists in the config file; if so: inform the user, suggest ensuring
- Check if it's already installed (if the path in the project exists, if it does remove it as we're about to reinstall it (from now on code for installing a new package and ensuring will be the same, so it should be good to abstract it))
- Check if we have it cached; if so: use it (copy it to our project or create a symlink)
- If it's not cached, check if the repository is valid on github (unless you also add custom git handlers which would be dope)
- In case of valid repository, cache it and either symlink or copy it to our local project as a git repo
- Update pulse.toml 
'''
@click.command
@click.argument("package", required=False, type=str)
@click.option("--all", "-a", is_flag=True, required=False, default=False, help="Ensures all packages are present.")
def install(package, all):
    '''Performs installation of a package.'''
    pckgi = PackageInstaller()
    if not all:
        pckgi.install_package(package)
    else:
        pckgi.install_all_packages()