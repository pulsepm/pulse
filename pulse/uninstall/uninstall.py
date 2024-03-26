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
@click.argument("package")
@click.option("-r", "--recursive", is_flag=True, default=False)
def uninstall(package: str, recursive: bool) -> None:
    """
    Uninstall pulse package.
    """
    re_package = re.split("/|@|==|:", package)
    if len(re_package) > 3:
        return click.echo("Using many options are not supported!")

    try:
        re_package[2]
    except:
        re_package.append(git_get.default_branch(re_package[0], re_package[1]))

    package_path = os.path.join(
        PACKAGE_PATH, f"{re_package[0]}/{re_package[1]}/{re_package[2]}"
    )
    if not os.path.exists(package_path):
        return click.echo(f"Package {package} was not found.")

    if recursive:
        dependencies = git_get.get_requirements(package_path)
        if dependencies:
            for dependency in dependencies:
                re_dependency = re.split("/|@|==|:", dependency)
                dep_path = os.path.join(
                    PACKAGE_PATH,
                    f"{re_dependency[0]}/{re_dependency[1]}/{re_dependency[2]}",
                )
                click.echo(f"Found dependency: {dependency}.")
                try:
                    re_dependency[2]
                except:
                    re_dependency.append(
                        git_get.default_branch(re_dependency[0], re_dependency[1])
                    )

                remove_if_plugin(re_dependency[0], re_dependency[1])
                requirements = git_get.get_requirements(dep_path)
                if requirements:
                    click.echo(f"Found requirements in {dependency}.")
                    for requirement in requirements:
                        re_requirement = re.split("/|@|==|:", requirement)
                        shutil.rmtree(
                            os.path.join(REQUIREMENTS_PATH, f"{re_requirement[1]}")
                        )
                        print(f"Deleted requirement: {re_requirement[1]}")

                shutil.rmtree(dep_path)
                os.rmdir(
                    os.path.join(PACKAGE_PATH, f"{re_dependency[0]}/{re_dependency[1]}")
                )
                print(f"Deleted dependency: {dependency}")

    with open(os.path.join(os.getcwd(), "pulse.toml"), "r") as file:
        data = toml.load(file)

    syntax: str = "==" if "==" in package else ":" if ":" in package else "@"
    data["requirements"]["live"].remove(
        f"{re_package[0]}/{re_package[1]}{syntax}{re_package[2]}"
    )
    with open(os.path.join(os.getcwd(), "pulse.toml"), "w") as file:
        toml.dump(data, file)

    shutil.rmtree(package_path)
    os.rmdir(os.path.join(PACKAGE_PATH, f"{re_package[0]}/{re_package[1]}"))
    remove_if_plugin(re_package[0], re_package[1])
    click.echo(f"Package {package} has been deleted.")


def remove_if_plugin(owner: str, repo: str) -> None:
    print("Looking for plugins..")
    try:
        plugins_dir = os.path.join(PLUGINS_PATH, f"{owner}/{repo}")
        for f_name in os.listdir(plugins_dir):
            if f_name.endswith(
                f"{'.dll' if platform.system() == 'Windows' else '.so'}"
            ):
                print(f"Found plugin: {f_name}!")
                shutil.rmtree(plugins_dir)
                print(f"Removed plugin: {f_name}.")

    except:
        return click.echo("Plugins not found.")
