import os

import click
import re
import toml
from pulse.core.core_dir import PACKAGE_PATH, REQUIREMENTS_PATH
import pulse.core.git.git_download as git_download
import pulse.core.git.git_get as git_get
import shutil


@click.command
@click.argument("package")
@click.option("-r", "--recursive", is_flag=True, default=False)
def uninstall(package: str, recursive: bool) -> None:
    """
    Uninstall pulse package.
    """
    re_package = re.split(
        "/|@|==|:", package
    )
    if len(re_package) > 3:
        return click.echo("Using many options are not supported!")

    try:
        re_package[2]
    except:
        re_package.append(git_get.default_branch(re_package[0], re_package[1]))

    package_path = os.path.join(PACKAGE_PATH, f"{re_package[0]}/{re_package[1]}/{re_package[2]}")
    if not os.path.exists(package_path):
        return click.echo(F"Package {package} was not found.")

    if recursive:
        dependencies = git_get.get_requirements(package_path)
        if dependencies:
            for dependency in dependencies:
                re_dependency = re.split("/|@|==|:", dependency)
                dep_path = os.path.join(PACKAGE_PATH, f"{re_dependency[0]}/{re_dependency[1]}/{re_dependency[2]}")
                click.echo(f"Found dependency: {dependency}.")
                try:
                    re_dependency[2]
                except:
                    re_dependency.append(git_get.default_branch(re_dependency[0], re_dependency[1]))

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
                print(f"Deleted dependency: {dependency}")

    with open(os.path.join(os.getcwd(), "pulse.toml"), "r") as file:
        data = toml.load(file)

    syntax: str = "==" if "==" in package else ":" if ":" in package else "@"
    data["requirements"]["live"].remove(f"{re_package[0]}/{re_package[1]}{syntax}{re_package[2]}")
    with open(os.path.join(os.getcwd(), "pulse.toml"), "w") as file:
        toml.dump(data, file)

    shutil.rmtree(package_path)
    click.echo(f"Package {package} has been deleted.")


