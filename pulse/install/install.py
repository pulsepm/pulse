import os

import click
import re
from pulse.core.core_dir import PACKAGE_PATH
import pulse.core.git.git_download as git_download
import pulse.core.git.git_get as git_get


@click.command
@click.argument("package")
def install(package: str) -> None:
    """
    Install a pulse package.

    """
    re_package = re.split(
        "/|@|==|:", package
    )  # ['Ykpauneu', 'pmtest' 'main / 1.0.0 / 7d3rfe']
    if len(re_package) > 3:
        return click.echo("Using many options are not supported!")

    package_path = os.path.join(PACKAGE_PATH, f"{re_package[0]}/{re_package[1]}")
    if os.path.exists(package_path):
        return click.echo(f"{re_package[0]}/{re_package[1]}'s already installed!")

    try:
        re_package[2]
    except:
        re_package.append(git_get.default_branch(re_package[0], re_package[1]))

    git_repo = git_get.get_github_repo(
        re_package[0], re_package[1], re_package[2], type=_package_type(package)
    )
    if not is_toml_package(git_repo):
        return click.echo(
            f"Couldn't find pulse.toml!\n{re_package[0]}/{re_package[1]}is not a Pulse package!"
        )
    click.echo(f"Installing: {package} ({re_package[2]})..")
    git_download.download_package(
        re_package[0],
        re_package[1],
        package_path,
        version=re_package[2],
        type=_package_type(package),
    )
    click.echo(
        f"Successfully installed the library: {re_package[0]}/{re_package[1]} ({re_package[2]})!"
    )


def is_toml_package(git_repo: list | dict) -> bool:
    if isinstance(git_repo, dict):
        git_repo = list(git_repo.values())

    is_toml: bool = False
    if isinstance(git_repo, list):
        for file in git_repo:
            try:
                file["path"]
            except:
                if isinstance(file, list):
                    for i in file:
                        if "pulse.toml" in i["path"]:
                            is_toml = True
                            break
            else:
                if "pulse.toml" in file["path"]:
                    is_toml = True
                    break

    return is_toml


def _package_type(package: str) -> str | None:
    type = None
    if "@" in package:
        type = "branch"

    if ":" in package:
        type = "commit"

    if "==" in package:
        type = "version"

    return type
