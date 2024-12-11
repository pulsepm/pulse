import os

import click
import re
from pulse.core.core_dir import PACKAGE_PATH
from typing import Literal
import git
import pulse.core.git.git_download as git_download
import pulse.core.git.git as git
import tomli
import tomli_w

from .content import (
    echo_retrieve_fail,
    get_package_syntax,
    get_package_type

)


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

    try:
        re_package[2]
    except:
        branch = git.default_branch(re_package)
        if not branch:
            return echo_retrieve_fail(re_package, branch)

        re_package.append(branch)

    package_path = os.path.join(PACKAGE_PATH, re_package[0], re_package[1])
    if os.path.exists(package_path):
        write_requirements(
            re_package[0],
            re_package[1],
            get_package_syntax(package),
            re_package[2],
        )
        return click.echo(f"{re_package[0]}/{re_package[1]}'s already installed!")

    git_repo = git.get_github_repo(
        re_package[0],
        re_package[1],
        re_package[2],
        get_package_syntax(package),
    )
    if not git_repo:
        return echo_retrieve_fail(re_package, git_repo)

    package_type = get_package_type(git_repo)
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
    write_requirements(
        re_package[0],
        re_package[1],
        get_package_syntax(package),
        re_package[2],
    )
    click.echo(
        f"Successfully installed library: {re_package[0]}/{re_package[1]} ({re_package[2]})!"
    )


def write_requirements(owner: str, repo: str, sign: str, syntax: str) -> None:
    package_name: str = f"{owner}/{repo}{sign}{syntax}"
    toml_path = os.path.join(os.getcwd(), "pulse.toml")

    if not os.path.exists(toml_path):
        tmp_file = open(toml_path, mode="w")
        tmp_file.close()

    with open(toml_path, "rb") as file:
        data = tomli.load(file)

    if "requirements" not in data:
        data["requirements"] = {"live": []}

    if package_name not in data["requirements"]["live"]:
        data["requirements"]["live"].append(package_name)
        with open(toml_path, "wb") as file:
            tomli_w.dump(data, file, multiline_strings=True)

