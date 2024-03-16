import os

import click
import re
from pulse.core.core_dir import PACKAGE_PATH
import pulse.core.git.git_download as git_download
import pulse.core.git.git_get as git_get

@click.command
@click.argument("package")
@click.option("--branch", help="Branch name", type=str)
@click.option("--commit", help="Commit", type=str)
@click.option("--version", help="Version", type=str)
def install(package: str, branch: str = None, commit: str = None, version: str = None) -> None:
    """
    Install a pulse package.

    """
    re_package = re.split('/|@|==|-', package) # ['Ykpauneu', 'pmtest' 'main / 1.0.0 / 7d3rfe']
    if len(re_package) > 3:
        return click.echo("Using many options are not supported!")

    package_path = os.path.join(PACKAGE_PATH, f"{re_package[0]}/{re_package[1]}")
    if os.path.exists(package_path):
        return click.echo(f"{re_package[0]}/{re_package[1]}'s already installed!")

    git_repo = git_get.get_github_repo(re_package[0], re_package[1], branch=branch, commit=commit, version=version)
    if not is_toml_package(git_repo):
        return click.echo(f"Couldn't find pulse.toml!\n{re_package[0]}/{re_package[1]}is not a Pulse package!")

    try:
        v_ = re_package[2]
    except:
        v_ = git_get.default_branch(re_package[0], re_package[1])

    click.echo(f"Installing: {package} ({v_})..")
    git_download.download_package(
        re_package[0],
        re_package[1],
        package_path,
        version=v_
    )
    click.echo(f"Successfully installed the library: {re_package[0]}/{re_package[1]} ({v_})!")

def is_toml_package(git_repo: list) -> bool:
    is_toml: bool = False
    for file in git_repo:
        if "pulse.toml" in file["path"]:
            is_toml = True
            break

    return is_toml
