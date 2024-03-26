import os

import click
import re
import toml
from pulse.core.core_dir import PACKAGE_PATH, REQUIREMENTS_PATH, PLUGINS_PATH
import pulse.core.git.git_download as git_download
import pulse.core.git.git_get as git_get
import shutil
import platform


@click.command
def ensure() -> None:
    """
    Ensures all packages are present.
    """
    current_path = os.getcwd()
    if not os.path.exists(os.path.join(current_path, "pulse.toml")):
        return click.echo("The pulse.toml file was not found..")

    with open(os.path.join(current_path, "pulse.toml")) as f:
        data = toml.load(f)

    if not "requirements" in data:
        return click.echo("No requirements were found in pulse.toml..")

    click.echo(f'Found: {len(data["requirements"]["live"])} requirements..')
    for requirement in data["requirements"]["live"]:
        re_package = re.split("/|@|==|:", requirement)
        try:
            re_package[2]
        except:
            re_package.append(git_get.default_branch(re_package[0], re_package[1]))
            click.echo(
                "No tag, commit, or branch was specified in the requirements. The default branch name will be used!"
            )

        package_path = os.path.join(
            PACKAGE_PATH, f"{re_package[0]}/{re_package[1]}/{re_package[2]}"
        )
        if not os.path.exists(package_path):
            click.echo(
                f"Package {re_package[0]}/{re_package[1]}/{re_package[2]} was not found, it will be installed."
            )
            git_download.download_package(
                re_package[0], re_package[1], package_path, re_package[2]
            )

        tmp_dir = os.path.join(REQUIREMENTS_PATH, f"{re_package[1]}")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
            is_plugin: bool = False
            plugins_path = os.path.join(
                PLUGINS_PATH, f"{re_package[0]}/{re_package[1]}"
            )
            for file in os.listdir(plugins_path):
                if file.endswith(
                    f"{'.dll' if platform.system() == 'Windows' else '.so'}"
                ):
                    click.echo(f"Found plugin: {file}!")
                    shutil.copy2(os.path.join(plugins_path, file), tmp_dir)
                    is_plugin = True
                    break

                if not is_plugin:
                    shutil.copy2(os.path.join(package_path, file), tmp_dir)

        else:
            click.echo("The requirement already exists..")

        print(
            f"Package {re_package[0]}/{re_package[1]} ({re_package[2]}) has been successfully migrated!"
        )
