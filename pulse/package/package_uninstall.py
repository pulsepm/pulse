import os

import click
import re
import toml
from pulse.core.core_dir import PACKAGE_PATH, REQUIREMENTS_PATH, PLUGINS_PATH
import pulse.package.package_utils as package_utils
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
        re_package[1]
    except:
        return click.echo("Incorrect entry of the package name.\nExample of package installation: author/repo.")

    try:
        re_package[2]
    except:
        branch = git_get.default_branch(re_package)
        if not branch:
            return package_utils.echo_retrieve_fail(re_package, branch)

        re_package.append(branch)

    package_path = os.path.join(
        PACKAGE_PATH, f"{re_package[0]}/{re_package[1]}/{re_package[2]}"
    )
    if not os.path.exists(package_path):
        return click.echo(f"Package {package} was not found.")

    if recursive:
        dependencies = git_get.get_requirements(package_path)
        if dependencies:
            remove_dependencies(dependencies)

    with open(os.path.join(os.getcwd(), "pulse.toml"), "r") as file:
        data = toml.load(file)

    package_name: str = f"{re_package[0]}/{re_package[1]}{package_utils.get_package_type(package)}{re_package[2]}"
    if package_name in data["requirements"]["live"]:
        data["requirements"]["live"].remove(
            package_name
        )
        with open(os.path.join(os.getcwd(), "pulse.toml"), "w") as file:
            toml.dump(data, file)

        click.echo(f"Removed package: {package_name} from pulse.toml.")

    remove_if_plugin(re_package[0], re_package[1])
    shutil.rmtree(package_path)
    os.rmdir(os.path.join(PACKAGE_PATH, f"{re_package[0]}/{re_package[1]}"))
    shutil.rmtree(os.path.join(REQUIREMENTS_PATH, re_package[1]), ignore_errors=True)
    click.echo(f"Package {package} has been deleted.")


def remove_dependencies(dependencies) -> None:
    for dependence in dependencies:
        dependence = re.split("/|@|==|:", dependence)
        try:
            dependence[1]
        except:
            print("Found incorrect package name.")
            continue

        try:
            dependence[2]
        except:
            branch = git_get.default_branch(dependence)
            if not branch:
                return package_utils.echo_retrieve_fail(dependence, branch)

            dependence.append(branch)

        dependence_ppc_path = os.path.join(
            PACKAGE_PATH, f"{dependence[0]}/{dependence[1]}/{dependence[2]}"
        )
        if not os.path.exists(dependence_ppc_path):
            click.echo(
                f"Package {dependence[0]}/{dependence[1]} ({dependence[2]}) was not found in {dependence_ppc_path}.."
            )
            continue

        remove_if_plugin(dependence[0], dependence[1])
        click.echo(
            f"Found dependence {dependence[0]}/{dependence[1]} ({dependence[2]}) in {dependence_ppc_path}!"
        )
        libs = git_get.get_requirements(dependence_ppc_path)
        if libs:
            remove_dependencies(libs)

        shutil.rmtree(dependence_ppc_path)
        shutil.rmtree(os.path.join(REQUIREMENTS_PATH, dependence[1]))
        os.rmdir(os.path.join(PACKAGE_PATH, f"{dependence[0]}/{dependence[1]}"))


def remove_plugins(directory: str) -> str:
    if os.path.exists(directory):
        for f_name in os.listdir(directory):
            if f_name.endswith(("dll", "so")):
                os.remove(os.path.join(directory, f_name))
                os.remove(os.path.join(REQUIREMENTS_PATH, f"plugins/{f_name}"))
                click.echo(f"Removed plugin: {f_name}.")

        shutil.rmtree(directory)
        return True

    else:
        return False


def remove_if_plugin(owner: str, repo: str) -> None:
    plugins_dir = os.path.join(PLUGINS_PATH, f"{owner}/{repo}")
    if not remove_plugins(plugins_dir):
        return click.echo(f"Plugins not found ({plugins_dir}).")
