import os
import tarfile
from zipfile import ZipFile
from platform import system
from pulse.core.core_dir import REQUIREMENTS_PATH, PLUGINS_PATH, PACKAGE_PATH, safe_open, CONFIG_FILE
from typing import Literal
from git import Repo
from pulse.core.git.git import valid_token
from pulse.package.unpack.unpack import extract_member
from pulse.package.package_handle import handle_extraction_zip, handle_extraction_tar

import re
import tomli
import requests
import pulse.core.git.git_get as git_get
import pulse.package.package_utils as package_utils
import shutil


def download_and_unzip_github_release(
    owner: str, repo: str, tag: str, asset_name: str, target_folder: str
) -> None:
    """
    Downloads and unzips a specific release asset from a GitHub repository.

    Parameters:
        owner (str): The owner (username or organization) of the GitHub repository.
        repo (str): The name of the GitHub repository.
        tag (str): The tag (version) of the release from which the asset will be downloaded.
        asset_name (str): The name of the asset to download.
        target_folder (str): The local path where the asset will be extracted.

    Returns:
        None
    """
    # Get the release information
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
    response = requests.get(api_url)

    if response.status_code != 200:
        print(
            f"Failed to get release information. HTTP Status Code: {response.status_code}"
        )
        return

    release_info = response.json()

    # Find the asset download URL
    asset_url = None
    for asset in release_info.get("assets", []):
        if asset["name"] == asset_name:
            asset_url = asset["browser_download_url"]
            break

    if asset_url is None:
        print(f"Asset '{asset_name}' not found in the release.")
        return

    # Download the asset
    try:
        response = requests.get(asset_url, allow_redirects=True)
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to the server: {e}")
        return

    if response.status_code == 200:
        print("Asset download successful")
        os.makedirs(target_folder, exist_ok=True)
        asset_path = os.path.join(target_folder, asset_name)

        with open(asset_path, "wb") as asset_file:
            asset_file.write(response.content)

        # Unzip the downloaded asset if it is a zip file
        if str(asset_name).endswith(".zip"):
            with ZipFile(asset_path, "r") as zip_ref:
                zip_ref.extractall(target_folder)
        elif str(asset_name).endswith(".tar.gz"):
            with tarfile.open(asset_path, "r:gz") as tar_ref:
                tar_ref.extractall(target_folder)
        else:
            print(f"Unsupported asset type: {asset_name}")
            return

        # Remove the downloaded asset file if needed
        os.remove(asset_path)
        print(f"Asset downloaded and extracted to: {target_folder}")

    else:
        print(f"Failed to download the asset. HTTP Status Code: {response.status_code}")


def gitpython_download(owner: str, repo: str, version: str, save_path, raw_syntax: str) -> Repo:
    token_file = safe_open(CONFIG_FILE, 'rb')
    token_data = tomli.load(token_file)
    token = token_data["token"]
     
    if valid_token(token):
        print("VALID")
    else:
        print("INVALID")
    if "#" in raw_syntax:
        git_repo = Repo.clone_from(
            f"https://{{{token}}}@github.com/{owner}/{repo}.git", save_path, single_branch=True
        )
        print(f"https://{{{token}}}@github.com/{owner}/{repo}.git")
        git_repo.head.reset(commit=version, index=True, working_tree=True)

    if ":" in raw_syntax:
        git_repo = Repo.clone_from(f"https://{{{token}}}@github.com/{owner}/{repo}", save_path)
        git = git_repo.git
        git.checkout(version)

    else:
        git_repo = Repo.clone_from(
            f"https://{{{token}}}@github.com/{owner}/{repo}.git",
            save_path,
            single_branch=True,
            branch=version,
        )
    
    return git_repo


def download_package(
    owner: str, repo: str, package_path: str, version: str, package_type: Literal["pulse", "sampctl", "master-pulse", "master-sampctl"], raw_syntax: str
) -> None:
    os.makedirs(package_path, exist_ok=True)
    package_dir = os.path.join(package_path, version)
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir, onerror=package_utils.on_rm_error)

    gitrepo = gitpython_download(owner, repo, version, package_dir, raw_syntax)

    fallback_package_file = True if package_type.startswith("master-") else False
    package_type.removeprefix("master-")
    
    if fallback_package_file:
        gitrepo.git.checkout("master")

    resource = git_get.get_package_resources(package_dir, package_type)

    if resource:
        print(f"Found resource for {owner}/{repo} ({package_type})!")
        download_resource(package_dir, resource, package_type)
    
    dependencies = git_get.get_requirements(package_dir, package_type)
    if dependencies:
        print(f"Found dependencies for {owner}/{repo} ({package_type})!")
        download_requirements(dependencies, package_type)

    requirements = os.path.join(REQUIREMENTS_PATH, repo)
    if os.path.exists(requirements):
        shutil.rmtree(requirements, onerror=package_utils.on_rm_error)

    shutil.copytree(package_dir, requirements)


def download_requirements(requirements: list, package_type: Literal["sampctl", "pulse"]) -> None:
    """
    Download requirements from pulse.toml or pawn.json
    """
    for requirement in requirements:
        re_requirement = re.split("/|@|:|#", requirement)
        try:
            re_requirement[1]
        except:
            print("Found incorrect package name.")
            continue

        try:
            branch = re_requirement[2]
        except:
            branch = git_get.default_branch(re_requirement)
            if not branch:
                package_utils.echo_retrieve_fail(re_requirement, branch)
                continue

            re_requirement.append(branch)

        pckg_path = os.path.join(
            PACKAGE_PATH, str(re_requirement[0]), str(re_requirement[1])
        )
        if os.path.exists(pckg_path):
            print(f"Found installed package: {re_requirement[0]}/{re_requirement[1]}..")
            continue

        pckg_path_version = os.path.join(pckg_path, re_requirement[2])
        gitpython_download(
            re_requirement[0],
            re_requirement[1],
            re_requirement[2],
            pckg_path_version,
            requirement
        )
        print(
            f"Installed dependency: {re_requirement[0]}/{re_requirement[1]} ({re_requirement[2]}) in {pckg_path_version}"
        )
        libs = git_get.get_requirements(pckg_path_version, package_type)
        save_path = os.path.join(REQUIREMENTS_PATH, re_requirement[1])
        if os.path.exists(save_path):
            shutil.rmtree(save_path, onerror=package_utils.on_rm_error)

        shutil.copytree(
            pckg_path_version, os.path.join(REQUIREMENTS_PATH, re_requirement[1])
        )
        if libs:
            print(
                f"Installing dependencies for {re_requirement[0]}/{re_requirement[1]}.."
            )
            download_requirements(libs, package_type)

        resource = git_get.get_package_resources(pckg_path_version, package_type)
        if resource:
            print(f"Found resource for {re_requirement[0]}/{re_requirement[1]} ({package_type})!")
            download_resource(pckg_path_version, resource, package_type)


def download_resource(origin_path, resource: tuple[str], package_type: Literal["sampctl", "pulse"]) -> None:
    owner, repo, release = resource
    cached_plugin_path = os.path.join(PLUGINS_PATH, owner, repo)
    os.makedirs(cached_plugin_path, exist_ok=True)

    request = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases/latest")
    response = request.json()
    assets = response["assets"]
    for asset in assets:
        print(release, asset["name"])
        if re.match(release, asset["name"]):
            download_url = asset["browser_download_url"]
            r = requests.get(download_url)
            archive = os.path.join(cached_plugin_path, asset["name"])
            with open(archive, "wb") as f:
                f.write(r.content)
            break

    print(
        f"Installed resource: {asset['name']} in {cached_plugin_path}"
    )
    
    cwd_path = os.path.join(REQUIREMENTS_PATH, "plugins")
    if not os.path.exists(cwd_path):
        os.makedirs(cwd_path)

    includes = git_get.get_resource_includes(origin_path, package_type)
    files = git_get.get_resource_files(origin_path, package_type)
    required_plugin = git_get.get_resource_plugins(origin_path, package_type)
    if not required_plugin and not (asset['name'].endswith(".so") or asset['name'].endswith(".dll")):
        return print("Plugins not found")
    
    if asset['name'].endswith(".so") or asset['name'].endswith(".dll"):
        source_path = os.path.join(cached_plugin_path, asset['name'])
        target_path = os.path.join(cwd_path, asset['name'])
        shutil.copy(source_path, target_path)
           
    if archive.string.endswith(".zip"):
        handle_extraction_zip(archive_path, includes, resource, files, required_plugin)

    if archive.string.endswith(".tar.gz"):
        handle_extraction_tar(archive_path, includes, resource, files, required_plugin)
