import os
from typing import Literal
import tarfile
from zipfile import ZipFile
import click
import re
import tomli
from pulse.core.core_dir import PACKAGE_PATH, REQUIREMENTS_PATH, PLUGINS_PATH, safe_open, CONFIG_FILE
import pulse.core.git.git_download as git_download
import pulse.package.content as content
import pulse.core.git.git as git
import shutil
from pulse.package.unpack.unpack import extract_member
from pulse.package.package_handle import handle_extraction_zip, handle_extraction_tar
from .package_uninstall import on_rm_error
import concurrent.futures


@click.command
def ensure() -> None:
    """
    Ensures all packages are present.
    """
    return ensure_packages()

def process_requirement(requirement):
    re_package = re.split("/|@|:|#", requirement)
    try:
        re_package[2]
    except IndexError:
        click.echo(
            f"No tag, commit, or branch was specified in the requirements for {re_package[0]}/{re_package[1]}. The default branch name will be used!"
        )

        branch = git.default_branch(re_package)
        if not branch:
            click.echo("Found incorrect package name.")
            return

        re_package.append(branch)

    if not is_package_installed(re_package[0], re_package[1], re_package[2]):
        click.echo(f"Package {re_package[0]}/{re_package[1]} ({re_package[2]}) was not found, it will be installed..")
        git_repo = git.get_github_repo(
            re_package[0],
            re_package[1],
            re_package[2],
            content.get_package_syntax(requirement),
        )
        if not git_repo:
            return content.echo_retrieve_fail(requirement, git_repo)

        package_type = content.get_package_type(git_repo)
        if not package_type:
            click.echo(
                f"Couldn't find pulse.toml or pawn.json!\n{re_package[0]}/{re_package[1]} Attempting to check the post-release changes"
            )
            git_repo = git.get_github_repo(
                re_package[0],
                re_package[1],
                re_package[2],
                False,
            )
            package_type = content.get_package_type(git_repo)

            if not package_type:
                return

            click.echo("Fallback has been found")
            package_type = "master-" + package_type

        click.echo(f"Installing: {re_package[0]}/{re_package[1]} ({re_package[2]})..")
        git_download.download_package(
            re_package[0],
            re_package[1],
            os.path.join(PACKAGE_PATH, re_package[0], re_package[1]),
            re_package[2],
            package_type,
            requirement
        )

    else:
        package_type = content.get_local_package_type(re_package[0], re_package[1], re_package[2])
        local_package_path = os.path.join(REQUIREMENTS_PATH, re_package[1])
        if os.path.exists(local_package_path):
            shutil.rmtree(local_package_path, onerror=on_rm_error)

        shutil.copytree(
            os.path.join(PACKAGE_PATH, re_package[0], re_package[1], re_package[2]),
            local_package_path,
        )

        dependencies = content.get_requirements(local_package_path, package_type)
        if dependencies:
            print(f"Found dependencies for {re_package[0]}/{re_package[1]} ({package_type})!")
            ensure_dependencies(dependencies)

        resource = content.get_package_resources(local_package_path, package_type)
        if resource:
            ensure_resource(resource, local_package_path, package_type)

# Main function to handle the concurrent execution
def process_all_requirements_concurrently(requirements):
    # Create a ThreadPoolExecutor with a max number of workers (adjust as needed)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit each requirement to be processed concurrently
        futures = [executor.submit(process_requirement, requirement) for requirement in requirements]

        # Wait for all futures to complete and handle any exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # This will raise an exception if the thread failed
            except Exception as e:
                click.echo(f"An error occurred: {e}")

# Example usage:


def ensure_packages() -> None:
    cwd_path = os.path.join(os.getcwd(), "pulse.toml")
    if not os.path.exists(cwd_path):
        return click.echo("The pulse.toml file was not found..")

    requirements = get_pulse_requirements(cwd_path)
    if not requirements:
        return click.echo("No requirements were found in pulse.toml..")

    click.echo(f'Found: {len(requirements)} requirements..')
    process_all_requirements_concurrently(requirements)

def ensure_dependencies(dependencies: list[str]) -> None:
    for raw_dependency in dependencies:
        dependency = re.split("/|@|:|#", raw_dependency)
        try:
            dependency[2]
        except:
            click.echo(
                f"No tag, commit, or branch was specified in the requirements for {dependency[0]}/{dependency[1]}. The default branch name will be used!"
            )

            branch = git.default_branch(dependency)
            if not branch:
                click.echo("Found incorrect package name.")
                continue

            dependency.append(branch)

        default_path = os.path.join(PACKAGE_PATH, dependency[0], dependency[1], dependency[2])
        dependency_path = os.path.join(REQUIREMENTS_PATH, dependency[1])
        if os.path.exists(dependency_path):
            print(f"Found installed dependency: {dependency[0]}/{dependency[1]}..")
            continue

        if not is_package_installed(dependency[0], dependency[1], dependency[2]):
            git_repo = git.get_github_repo(
                dependency[0],
                dependency[1],
                dependency[2],
                content.get_package_syntax(raw_dependency),
            )
            if not git_repo:
                return content.echo_retrieve_fail(raw_dependency, git_repo)

            package_type = content.get_package_type(git_repo)
            if not package_type:
                click.echo(
                    f"Couldn't find pulse.toml or pawn.json!\n{dependency[0]}/{dependency[1]} is not Pulse / sampctl package!"
                )
                continue

            click.echo(f"Installing: {dependency[0]}/{dependency[1]} ({dependency[2]})..")
            git_download.download_package(
                dependency[0],
                dependency[1],
                os.path.join(PACKAGE_PATH, dependency[0], dependency[1]),
                dependency[2],
                package_type,
                raw_dependency
            )
        else:
            package_type = content.get_local_package_type(dependency[0], dependency[1], dependency[2])
            shutil.copytree(
                default_path,
                dependency_path,
                dirs_exist_ok=True
            )

            libs = content.get_requirements(default_path, package_type)
            if libs:
                ensure_dependencies(libs)

            resource = content.get_package_resources(default_path, package_type)
            if resource:
                ensure_resource(resource, default_path, package_type)

        click.echo(f"Migrated {dependency[0]}/{dependency[1]} ({dependency[2]})..")


def ensure_resource(resource: tuple[str], origin_path, package_type: Literal["pulse", "sampctl"]) -> None:
    plugin_path = os.path.join(PLUGINS_PATH, resource[0], resource[1])
    file_name = resource[2]
    cwd_path = os.path.join(REQUIREMENTS_PATH, "plugins")
    if not os.path.exists(cwd_path):
        os.makedirs(cwd_path)  

    includes = content.get_resource_includes(origin_path, package_type)
    files = content.get_resource_files(origin_path, package_type)

    required_plugin = content.get_resource_plugins(origin_path, package_type)
    if not required_plugin and not (file_name.endswith(".so") or file_name.endswith(".dll")):
        return

    if file_name.endswith(".so") or file_name.endswith(".dll"):
        source_path = os.path.join(plugin_path, file_name)
        target_path = os.path.join(cwd_path, file_name)
        shutil.copy(source_path, target_path)
    
    cwd_path = os.path.join(REQUIREMENTS_PATH, "plugins")
    if not os.path.exists(cwd_path):
        os.makedirs(cwd_path)

    required_plugin = content.get_resource_plugins(origin_path, package_type)
    if not required_plugin and not (file_name.endswith(".so") or file_name.endswith(".dll")):
        return
    
    for file in os.listdir(plugin_path):
        archive = re.match(resource[2], file)
        archive_path = os.path.join(plugin_path, archive.string)

        if archive.string.endswith(".zip"):
            handle_extraction_zip(archive_path, includes, resource, files, required_plugin)

        if archive.string.endswith(".tar.gz"):
            handle_extraction_tar(archive_path, includes, resource, files, required_plugin)

def get_pulse_requirements(path) -> dict[str] | bool:
    with open(path, mode="rb") as f:
        data = tomli.load(f)

    if not "requirements" in data:
        return False

    return data["requirements"]["live"]


def is_package_installed(owner: str, repo: str, version: str) -> bool:
    package_path = os.path.join(PACKAGE_PATH, str(owner), str(repo), str(version))
    if os.path.exists(package_path):
        return True

    return False