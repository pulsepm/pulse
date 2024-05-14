import os

import click
import re
from pulse.core.core_dir import PACKAGE_PATH, REQUIREMENTS_PATH, PLUGINS_PATH
import pulse.package.package_utils as package_utils
import pulse.core.git.git_get as git_get
import shutil


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
        return click.echo(
            "Incorrect entry of the package name.\nExample of package installation: author/repo."
        )

    try:
        re_package[2]
    except:
        branch = git_get.default_branch(re_package)
        if not branch:
            return package_utils.echo_retrieve_fail(re_package, branch)

        re_package.append(branch)

    package_path = os.path.join(
        PACKAGE_PATH, re_package[0], re_package[1], re_package[2]
    )
    if not os.path.exists(package_path):
        return click.echo(f"Package {package} was not found.")

    package_type = package_utils.get_local_package_type(re_package[0], re_package[1], re_package[2])
    if recursive:
        dependencies = git_get.get_requirements(package_path, package_type)
        if dependencies:
            print(f"Found dependencies for {re_package[0]}/{re_package[1]} ({package_type})!")
            remove_dependencies(dependencies)

    resource = git_get.get_package_resources(package_path, package_type)
    if resource:
        print(f"Found resource for {re_package[0]}/{re_package[1]} ({package_type})!")
        remove_resource(package_path, resource, package_type, recursive=recursive)

    package_utils.remove_requirements(
        re_package[0],
        re_package[1],
        package_utils.get_package_syntax(package),
        re_package[2]
    )

    remove_package(re_package[0], re_package[1])
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
            PACKAGE_PATH, dependence[0], dependence[1], dependence[2]
        )
        if not os.path.exists(dependence_ppc_path):
            click.echo(
                f"Package {dependence[0]}/{dependence[1]} ({dependence[2]}) was not found in {dependence_ppc_path}.."
            )
            continue

        click.echo(
            f"Found dependence {dependence[0]}/{dependence[1]} ({dependence[2]}) in {dependence_ppc_path}!"
        )
        dependence_type = package_utils.get_local_package_type(dependence[0], dependence[1], dependence[2])
        libs = git_get.get_requirements(dependence_ppc_path, dependence_type)
        if libs:
            remove_dependencies(libs)

        resource = git_get.get_package_resources(dependence_ppc_path, dependence_type)
        if resource:
            remove_resource(resource)

        remove_package(dependence[0], dependence[1])


def remove_resource(origin_path, resource: tuple[str], package_type, recursive: bool = False) -> None:
    owner, repo, release = resource
    if recursive:
        shutil.rmtree(os.path.join(PLUGINS_PATH, owner, repo))

    plugin = git_get.get_resource_plugins(origin_path, package_type)
    plugin_path = os.path.join(
        REQUIREMENTS_PATH, "plugins", package_utils.get_resource_file("".join(plugin))
    )
    if os.path.isfile(plugin_path):
        os.remove(plugin_path)


def remove_package(owner: str, repo: str) -> None:
    shutil.rmtree(os.path.join(PACKAGE_PATH, owner, repo), onerror=package_utils.on_rm_error)
    shutil.rmtree(os.path.join(REQUIREMENTS_PATH, repo), onerror=package_utils.on_rm_error)
