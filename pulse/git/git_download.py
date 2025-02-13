import os
import tarfile
from zipfile import ZipFile
from platform import system
from pulse.core.core_dir import REQUIREMENTS_PATH, PLUGINS_PATH, PACKAGE_PATH, CONFIG_FILE
from typing import Literal
from git import Repo
from pulse.git.git import valid_token, default_branch
from pulse.package.unpack.unpack import extract_member
from pulse.package.package_handle import handle_extraction_zip, handle_extraction_tar

import re
import tomli
import requests
import shutil


def download_and_unzip_github_release(
    owner: str, repo: str, tag: str, asset_name: str, target_folder: str, remove_asset: bool = True
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
        elif str(asset_name).endswith(".dll") or str(asset_name).endswith(".so"):
            print(f"Moving {asset_path} to {target_folder}")
        else:
            print(f"Unsupported asset type: {asset_name}")
            return

        # Remove the downloaded asset file if needed
        if remove_asset:
            os.remove(asset_path)
            
        print(f"Asset downloaded and extracted to: {target_folder}")

    else:
        print(f"Failed to download the asset. HTTP Status Code: {response.status_code}")


def download_github_release(
    owner: str, repo: str, tag: str, asset_name: str, target_folder: str
) -> str | None:
    """
    Downloads a specific release asset from a GitHub repository.

    Parameters:
        owner (str): The owner (username or organization) of the GitHub repository.
        repo (str): The name of the GitHub repository.
        tag (str): The tag (version) of the release from which the asset will be downloaded.
        asset_name (str): The name of the asset to download.
        target_folder (str): The local path where the asset will be saved.

    Returns:
        str | None: Path to the downloaded asset if successful, None if failed
    """
    # Get the release information
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
    response = requests.get(api_url)

    if response.status_code != 200:
        print(f"Failed to get release information. HTTP Status Code: {response.status_code}")
        return None

    release_info = response.json()

    # Find the asset download URL
    asset_url = None
    for asset in release_info.get("assets", []):
        if asset["name"] == asset_name:
            asset_url = asset["browser_download_url"]
            break

    if asset_url is None:
        print(f"Asset '{asset_name}' not found in the release.")
        return None

    # Download the asset
    try:
        response = requests.get(asset_url, allow_redirects=True)
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to the server: {e}")
        return None

    if response.status_code != 200:
        print(f"Failed to download the asset. HTTP Status Code: {response.status_code}")
        return None

    print("Asset download successful")
    os.makedirs(target_folder, exist_ok=True)
    asset_path = os.path.join(target_folder, asset_name)

    with open(asset_path, "wb") as asset_file:
        asset_file.write(response.content)

    return asset_path

def extract_asset(asset_path: str, target_folder: str, remove_asset: bool = True) -> bool:
    """
    Extracts a downloaded asset to the target folder.

    Parameters:
        asset_path (str): Path to the downloaded asset
        target_folder (str): The local path where the asset will be extracted
        remove_asset (bool): Whether to remove the downloaded asset after extraction

    Returns:
        bool: True if extraction was successful, False otherwise
    """
    asset_name = os.path.basename(asset_path)

    try:
        if asset_name.endswith(".zip"):
            with ZipFile(asset_path, "r") as zip_ref:
                zip_ref.extractall(target_folder)
        elif asset_name.endswith(".tar.gz"):
            with tarfile.open(asset_path, "r:gz") as tar_ref:
                tar_ref.extractall(target_folder)
        elif asset_name.endswith(".dll") or asset_name.endswith(".so"):
            pass
        else:
            print(f"Unsupported asset type: {asset_name}")
            return False

        if remove_asset:
            os.remove(asset_path)

        print(f"Asset extracted to: {target_folder}")
        return True

    except Exception as e:
        print(f"Failed to extract asset: {e}")
        return False