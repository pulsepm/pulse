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

        ensure_path = os.path.join(REQUIREMENTS_PATH, re_package[1])
        shutil.copytree(package_path, ensure_path, dirs_exist_ok=True)
        plugins_path = os.path.join(PLUGINS_PATH, f"{re_package[0]}/{re_package[1]}")
        if os.path.exists(plugins_path):
            ensure_plugin(plugins_path)

        dependencies = git_get.get_requirements(package_path)
        if dependencies:
            ensure_dependencies(dependencies)

        print(
            f"Package {re_package[0]}/{re_package[1]} ({re_package[2]}) has been successfully migrated!"
        )

def ensure_dependencies(dependencies) -> None:
    for dependency in dependencies:
        dependency = re.split("/|@|==|:", dependency)

    default_path = os.path.join(PACKAGE_PATH, f"{dependency[0]}/{dependency[1]}/{dependency[2]}")
    dep_plugins = os.path.join(PLUGINS_PATH, f"{dependency[0]}/{dependency[1]}")
    if os.path.exists(dep_plugins):
        ensure_plugin(dep_plugins)

    shutil.copytree(default_path, os.path.join(REQUIREMENTS_PATH, dependency[1]), dirs_exist_ok=True)
    click.echo(f"Migrated {dependency[0]}/{dependency[1]} ({dependency[2]})..")
    libs = git_get.get_requirements(default_path)
    if libs:
        ensure_dependencies(libs)


def ensure_plugin(directory) -> None:
    ensure_plugin_path = os.path.join(REQUIREMENTS_PATH, "plugins")
    if not os.path.exists(ensure_plugin_path):
        os.makedirs(ensure_plugin_path)

    for f_name in os.listdir(directory):
        if f_name.endswith(("dll", "so")):
            print(f"Found plugin: {f_name} in {directory}!")
            shutil.copy2(os.path.join(directory, f_name), ensure_plugin_path)
