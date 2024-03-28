import os
import tarfile
from zipfile import ZipFile
from platform import system
from pulse.core.core_dir import REQUIREMENTS_PATH, PLUGINS_PATH, PACKAGE_PATH
from io import BytesIO

import re
import requests
import pulse.core.git.git_get as git_get
import toml
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


def download_package(owner: str, repo: str, package_path: str, version: str) -> None:
    os.makedirs(package_path)
    try:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/{'zipball' if system() == 'Windows' else 'tarball'}/{version}",
            stream=True,
        )

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    if system() == "Windows":
        with ZipFile(BytesIO(response.content)) as z:
            z.extractall(package_path)

    if system() == "Linux":
        with tarfile.open(BytesIO(response.content), "r:gz") as tar_ref:
            tar_ref.extractall(package_path)

    package_dir = os.path.join(package_path, version)
    os.rename(os.path.join(package_path, os.listdir(package_path)[0]), package_dir)
    package_dir = copy_if_plugin(owner, repo, package_dir)
    libs = git_get.get_requirements(package_dir)
    if libs:
        print(f"Found dependencies for {owner}/{repo}!\nInstalling..")
        download_requirements(libs)

    requirements = os.path.join(REQUIREMENTS_PATH, repo)
    shutil.copytree(package_dir, requirements)


def download_requirements(requirements: list) -> None:
    """
    Download requirements from pulse package
    """
    for requirement in requirements:
        re_requirement = re.split("/|@|==|:", requirement)
        try:
            branch = re_requirement[2]
        except:
            branch = git_get.default_branch(re_requirement[0], re_requirement[1])

        install_path = os.path.join(PACKAGE_PATH, f"{re_requirement[0]}/{re_requirement[1]}")
        try:
            response = requests.get(
                f"https://api.github.com/repos/{re_requirement[0]}/{re_requirement[1]}/{'zipball' if system() == 'Windows' else 'tarball'}/{branch}",
                stream=True,
            )

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        if os.path.exists(install_path):
            print(f"Found installed package: {re_requirement[0]}/{re_requirement[1]}..")
            continue

        os.makedirs(install_path, exist_ok=True)
        if system() == "Windows":
            with ZipFile(BytesIO(response.content)) as z:
                z.extractall(install_path)

        if system() == "Linux":
            with tarfile.open(BytesIO(response.content), "r:gz") as tar_ref:
                tar_ref.extractall(install_path)

        print(
            f"Installed dependency: {os.listdir(install_path)[0]} in {install_path}"
        )
        install_path_with_ver = os.path.join(install_path, re_requirement[2])
        os.rename(
            os.path.join(install_path, os.listdir(install_path)[0]),
            install_path_with_ver,
        )
        install_path_with_ver = copy_if_plugin(re_requirement[0], re_requirement[1], install_path_with_ver)
        libs = git_get.get_requirements(install_path_with_ver)
        shutil.copytree(install_path_with_ver, os.path.join(REQUIREMENTS_PATH, re_requirement[1]))
        print
        if libs:
            print(f"Found dependencies for {re_requirement[0]}/{re_requirement[1]}!\nInstalling..")
            download_requirements(libs)


def copy_if_plugin(owner: str, repo: str, directory):
    for f_name in os.listdir(directory):
        if f_name.endswith(f"{'.dll' if system() == 'Windows' else '.so'}"):
            print(f"Found plugin: {f_name} in {directory}!")
            tmp_dir = os.path.join(PLUGINS_PATH, f"{owner}/{repo}")
            tmp_reqirements = os.path.join(REQUIREMENTS_PATH, "plugins")
            os.makedirs(tmp_reqirements, exist_ok=True)
            if os.path.exists(tmp_dir):
                print("The plugin has already been installed..")
                break

            else:
                os.makedirs(tmp_dir)
                shutil.copy2(os.path.join(directory, f_name), tmp_dir)
                shutil.copy2(os.path.join(directory, f_name), tmp_reqirements)
                os.remove(os.path.join(directory, f_name))
                break

    return directory
