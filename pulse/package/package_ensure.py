import os
from typing import Literal
import tarfile
from zipfile import ZipFile
import click
import re
import tomli
from pulse.core.core_dir import PACKAGE_PATH, REQUIREMENTS_PATH, PLUGINS_PATH, safe_open
import pulse.core.git.git_download as git_download
import pulse.core.git.git_get as git_get
import pulse.package.package_utils as package_utils
import shutil
from pulse.package.unpack.unpack import extract_member
from pulse.package.package_handle import handle_extraction_zip, handle_extraction_tar
from concurrent.futures import ThreadPoolExecutor



@click.command
def ensure() -> None:
    """
    Ensures all packages are present.
    """
    return ensure_packages()


def ensure_packages() -> None:
    cwd_path = os.path.join(os.getcwd(), "pulse.toml")
    if not os.path.exists(cwd_path):
        return click.echo("The pulse.toml file was not found..")

    requirements = get_pulse_requirements(cwd_path)
    if not requirements:
        return click.echo("No requirements were found in pulse.toml..")

    click.echo(f'Found: {len(requirements)} requirements..')
    pck_to_dwn = []
    
    for requirement in requirements:
        re_package = re.split("/|@|:|#", requirement)
        try:
            re_package[2]
        except:
            click.echo(
                f"No tag, commit, or branch was specified in the requirements for {re_package[0]}/{re_package[1]}. The default branch name will be used!"
            )

            branch = git_get.default_branch(re_package)
            if not branch:
                click.echo("Found incorrect package name.")
                continue

            re_package.append(branch)

        if not is_package_installed(re_package[0], re_package[1], re_package[2]):
            click.echo(f"Package {re_package[0]}/{re_package[1]} ({re_package[2]}) was not found, it will be installed..")
            git_repo = git_get.get_github_repo(
                re_package[0],
                re_package[1],
                re_package[2],
                package_utils.get_package_syntax(requirement),
            )
            if not git_repo:
                return package_utils.echo_retrieve_fail(requirement, git_repo)

            package_type = package_utils.get_package_type(git_repo)
            if not package_type:
                # Check if the pawn.json/pulse.toml has been made available after the release
                click.echo(
                    f"Couldn't find pulse.toml or pawn.json!\n{re_package[0]}/{re_package[1]} Attempting to check the post-release changes"
                )
                git_repo = git_get.get_github_repo(
                   re_package[0],
                    re_package[1],
                    re_package[2],
                    False,
                )
                package_type = package_utils.get_package_type(git_repo)
                
                if not package_type:
                    continue
                
                click.echo("Fallback has been found")
                package_type = "master-" + package_type 

            pck_to_dwn.append(
                [re_package[0], re_package[1], os.path.join(PACKAGE_PATH, re_package[0], re_package[1]), re_package[2], package_type, requirement]
            )

        else:
            package_type = package_utils.get_local_package_type(re_package[0], re_package[1], re_package[2])
            local_package_path = os.path.join(REQUIREMENTS_PATH, re_package[1])
            if os.path.exists(local_package_path):
                shutil.rmtree(local_package_path, onerror=package_utils.on_rm_error)

            shutil.copytree(
                os.path.join(PACKAGE_PATH, re_package[0], re_package[1], re_package[2]),
                local_package_path,
            )

            dependencies = git_get.get_requirements(local_package_path, package_type)
            if dependencies:
                print(f"Found dependencies for {re_package[0]}/{re_package[1]} ({package_type})!")
                ensure_dependencies(dependencies)

            resource = git_get.get_package_resources(local_package_path, package_type)
            if resource:
                ensure_resource(resource, local_package_path, package_type)
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        click.echo(f"Installing the dependencies..")
        futures = []
        for package in pck_to_dwn:
            # Unpack the list for the arguments of download_package
            futures.append(executor.submit(git_download.download_package, *package))
        
        # Optionally wait for all tasks to complete and handle results
        for future in futures:
            try:
                future.result()  # This will raise any exceptions that occurred in download_package
            except ConnectionResetError as e:
                print(f"Connection reset error on attempt {e}")
           

            except KeyError as e:
                print(f"Key error encountered while processing: {e}")

            except Exception as e:
                print(f"An error occurred while downloading: {e}")
                break  


def ensure_dependencies(dependencies: list[str]) -> None:
    for raw_dependency in dependencies:
        dependency = re.split("/|@|:|#", raw_dependency)
        try:
            dependency[2]
        except:
            click.echo(
                f"No tag, commit, or branch was specified in the requirements for {dependency[0]}/{dependency[1]}. The default branch name will be used!"
            )

            branch = git_get.default_branch(dependency)
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
            git_repo = git_get.get_github_repo(
                dependency[0],
                dependency[1],
                dependency[2],
                package_utils.get_package_syntax(raw_dependency),
            )
            if not git_repo:
                return package_utils.echo_retrieve_fail(raw_dependency, git_repo)

            package_type = package_utils.get_package_type(git_repo)
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
            package_type = package_utils.get_local_package_type(dependency[0], dependency[1], dependency[2])
            shutil.copytree(
                default_path,
                dependency_path,
                dirs_exist_ok=True
            )

            libs = git_get.get_requirements(default_path, package_type)
            if libs:
                ensure_dependencies(libs)

            resource = git_get.get_package_resources(default_path, package_type)
            if resource:
                ensure_resource(resource, default_path, package_type)

        click.echo(f"Migrated {dependency[0]}/{dependency[1]} ({dependency[2]})..")


def ensure_resource(resource: tuple[str], origin_path, package_type: Literal["pulse", "sampctl"]) -> None:
    plugin_path = os.path.join(PLUGINS_PATH, resource[0], resource[1])
    file_name = resource[2]
    cwd_path = os.path.join(REQUIREMENTS_PATH, "plugins")
    if not os.path.exists(cwd_path):
        os.makedirs(cwd_path)  

    includes = git_get.get_resource_includes(origin_path, package_type)
    files = git_get.get_resource_files(origin_path, package_type)

    required_plugin = git_get.get_resource_plugins(origin_path, package_type)
    if not required_plugin and not (file_name.endswith(".so") or file_name.endswith(".dll")):
        return

    if file_name.endswith(".so") or file_name.endswith(".dll"):
        source_path = os.path.join(plugin_path, file_name)
        target_path = os.path.join(cwd_path, file_name)
        shutil.copy(source_path, target_path)
    
    cwd_path = os.path.join(REQUIREMENTS_PATH, "plugins")
    if not os.path.exists(cwd_path):
        os.makedirs(cwd_path)

    required_plugin = git_get.get_resource_plugins(origin_path, package_type)
    if not required_plugin and not (file_name.endswith(".so") or file_name.endswith(".dll")):
        return
    
    for file in os.listdir(plugin_path):
        archive = re.match(resource[2], file)
        if archive:
            break
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