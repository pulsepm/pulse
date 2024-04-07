import os

import click
import re
from pulse.core.core_dir import PACKAGE_PATH
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
        "/|@|==|:", package
    )  # ['Ykpauneu', 'pmtest' 'main / 1.0.0 / 7d3rfe']
    if len(re_package) > 3:
        return click.echo("Using many options are not supported!")

    try:
        re_package[1]
    except:
        return click.echo("Incorrect entry of the package name.\nExample of package installation: author/repo.")

    package_path = os.path.join(PACKAGE_PATH, f"{re_package[0]}/{re_package[1]}")
    if os.path.exists(package_path):
        return click.echo(f"{re_package[0]}/{re_package[1]}'s already installed!")

    try:
        re_package[2]
    except:
        branch = git_get.default_branch(re_package)
        if not branch:
            return package_utils.echo_retrieve_fail(re_package, branch)

        re_package.append(branch)

    git_repo = git_get.get_github_repo(re_package, package_utils.get_package_type(package))
    if not git_repo:
        return package_utils.echo_retrieve_fail(re_package, branch)

    if not is_toml_package(git_repo):
        return click.echo(
            f"Couldn't find pulse.toml!\n{re_package[0]}/{re_package[1]}is not a Pulse package!"
        )
    click.echo(f"Installing: {re_package[0]}/{re_package[1]} ({re_package[2]})..")
    git_download.download_package(
        re_package[0],
        re_package[1],
        package_path,
        version=re_package[2],
    )
    package_utils.write_requirements(re_package[0], re_package[1], package_utils.get_package_type(package), re_package[2])
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
