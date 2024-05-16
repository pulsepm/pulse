import os
import tarfile
import stat
from zipfile import ZipFile
from platform import system
from pulse.core.core_dir import REQUIREMENTS_PATH, PLUGINS_PATH, PACKAGE_PATH
from typing import Literal
from git import Repo

import re
import requests
import pulse.core.git.git_get as git_get
import pulse.package.package_utils as package_utils
import shutil
import logging
import pulse.stroke.stroke as stroke


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

    if response.ok:
        logging.fatal(f"Failed to get release information. HTTP Status Code: {response.status_code}")
        stroke.dump(6)
        return

    release_info = response.json()

    # Find the asset download URL
    asset_url = None
    for asset in release_info.get("assets", []):
        if asset["name"] == asset_name:
            asset_url = asset["browser_download_url"]
            break

    if asset_url is None:
        logging.fatal(f"Asset '{asset_name}' not found in the release.")
        stroke.dump(3)
        return

    # Download the asset
    try:
        response = requests.get(asset_url, allow_redirects=True)
    except requests.exceptions.RequestException as e:
        logging.fatal(f"Failed to connect to the server: {e}")
        stroke.dump(5)
        return

    if response.status_code == 200:
        logging.debug("Asset downloading started..")
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
            logging.fatal(f"Unsupported asset type: {asset_name}")
            stroke.dump(3)
            return

        # Remove the downloaded asset file if needed
        os.remove(asset_path)
        logging.info(f"Asset downloaded and extracted to: {target_folder}")

    else:
        logging.fatal(f"Failed to download the asset. HTTP Status Code: {response.status_code}")
        stroke.dump(6)


def download_package(
    owner: str, repo: str, package_path: str, version: str, is_commit: bool = False
) -> None:
    logging.debug(f"Cloning repository ({owner}/{repo})..")
    os.makedirs(package_path, exist_ok=True)
    package_dir = os.path.join(package_path, version)
    if not is_commit:
        Repo.clone_from(
            f"https://github.com/{owner}/{repo}.git",
            save_path,
            single_branch=True,
            branch=version,
        )


def download_package(
    owner: str, repo: str, package_path: str, version: str, package_type: Literal["pulse", "sampctl"], raw_syntax: str
) -> None:
    os.makedirs(package_path, exist_ok=True)
    package_dir = os.path.join(package_path, version)
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir, onerror=package_utils.on_rm_error)

    gitpython_download(owner, repo, version, package_dir, raw_syntax)
    dependencies = git_get.get_requirements(package_dir, package_type)
    if dependencies:
        logging.info(f"Found dependencies for {owner}/{repo}!")
        download_requirements(dependencies)

    requirements = os.path.join(REQUIREMENTS_PATH, repo)
    if os.path.exists(requirements):
        shutil.rmtree(requirements, onerror=package_utils.on_rm_error)

    shutil.copytree(package_dir, requirements)


def download_requirements(requirements: list, package_type: Literal["sampctl", "pulse"]) -> None:
    """
    Download requirements from pulse.toml or pawn.json
    """
    for requirement in requirements:
        re_requirement = re.split("/|@|==|:", requirement)
        try:
            re_requirement[1]
        except:
            logging.warning("Found incorrect package name.")
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
            PACKAGE_PATH, re_requirement[0], re_requirement[1]
        )
        if os.path.exists(pckg_path):
            logging.info(f"Found installed package: {re_requirement[0]}/{re_requirement[1]}..")
            continue

        pckg_path_version = os.path.join(pckg_path, re_requirement[2])
        logging.debug(f"Cloning repository as dependency ({re_requirement[0]}/{re_requirement[1]})..")
        Repo.clone_from(
            f"https://github.com/{re_requirement[0]}/{re_requirement[1]}.git",
            pckg_path_version,
            requirement
        )
        logging.info(
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
            logging.info(
                f"Found dependencies for {re_requirement[0]}/{re_requirement[1]}!\nInstalling.."
            )
            download_requirements(libs)


def copy_if_plugin(owner: str, repo: str, directory):
    for f_name in os.listdir(directory):
        if f_name.endswith(("dll", "so")):
            if (
                system() == "Windows"
                and f_name.endswith("so")
                or system() == "Linux"
                and f_name.endswith("dll")
            ):
                os.remove(os.path.join(directory, f_name))
                continue

            logging.info(f"Found plugin: {f_name} in {directory}!")
            tmp_dir = os.path.join(PLUGINS_PATH, f"{owner}/{repo}")
            tmp_reqirements = os.path.join(REQUIREMENTS_PATH, "plugins")
            os.makedirs(tmp_reqirements, exist_ok=True)
            os.makedirs(tmp_dir, exist_ok=True)
            shutil.copy2(os.path.join(directory, f_name), tmp_dir)
            shutil.copy2(os.path.join(directory, f_name), tmp_reqirements)
            os.remove(os.path.join(directory, f_name))
            continue

    return directory


def copy_to_cwd_requirements(origin_path, package_name: str) -> None:
    return shutil.copytree(
        origin_path, os.path.join(REQUIREMENTS_PATH, package_name), dirs_exist_ok=True
    )
