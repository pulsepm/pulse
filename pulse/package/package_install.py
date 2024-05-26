import os

import click
import re
from pulse.core.core_dir import PACKAGE_PATH
from typing import Literal
import git
import pulse.core.git.git_download as git_download
import pulse.core.git.git_get as git_get
import pulse.package.package_utils as package_utils


@click.command
@click.argument("package")
def install(package: str) -> None:
    """
    Install a pulse package.
    """

    re_package = re.split(
        "/|@|:|#", package
    )  # ['Ykpauneu', 'pmtest' 'main / 1.0.0 / 7d3rfe']
    if len(re_package) > 3:
        return click.echo("Using many options are not supported!")

    try:
        re_package[1]
    except:
        return click.echo(
            "Incorrect entry of the package name.\nExample of command: pulse install Author/Repo"
        )

    package_path = os.path.join(PACKAGE_PATH, re_package[0], re_package[1])
    if os.path.exists(package_path):
        return click.echo(f"{re_package[0]}/{re_package[1]}'s already installed!")

    try:
        re_package[2]
    except:
        branch = git_get.default_branch(re_package)
        if not branch:
            return package_utils.echo_retrieve_fail(re_package, branch)

        re_package.append(branch)

    git_repo = git_get.get_github_repo(
        re_package[0],
        re_package[1],
        re_package[2],
        package_utils.get_package_syntax(package),
    )
    if not git_repo:
        return package_utils.echo_retrieve_fail(re_package, git_repo)

    package_type = package_utils.get_package_type(git_repo)
    if not package_type:
        return click.echo(
            f"Couldn't find pulse.toml or pawn.json!\n{re_package[0]}/{re_package[1]} is not Pulse / sampctl package!"
        )
    click.echo(f"Installing: {re_package[0]}/{re_package[1]} ({re_package[2]})..")
    git_download.download_package(
        re_package[0],
        re_package[1],
        package_path,
        re_package[2],
        package_type,
        package
    )
    package_utils.write_requirements(
        re_package[0],
        re_package[1],
        package_utils.get_package_syntax(package),
        re_package[2],
    )
    click.echo(
        f"Successfully installed library: {re_package[0]}/{re_package[1]} ({re_package[2]})!"
    )
