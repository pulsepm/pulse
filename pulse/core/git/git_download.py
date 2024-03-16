import os
import tarfile
from zipfile import ZipFile
from platform import system
from pulse.core.core_dir import REQUIREMENTS_PATH
from io import BytesIO

import re
import requests
import pulse.core.git.git_get as git_get
import toml


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
    libs = get_requirements(package_dir)
    if libs:
        download_requirements(libs)


def download_requirements(requirements: list) -> None:
    """
    Download requirements from pulse package
    """
    for requirement in requirements:
        req = re.split("/|@|==|:", requirement)
        dependency_path = os.path.join(REQUIREMENTS_PATH, f"{req[0]}/{req[1]}")
        if not os.path.exists(dependency_path):
            os.makedirs(dependency_path)
            try:
                branch = req[2]
            except:
                branch = git_get.default_branch(req[0], req[1])
            try:
                response = requests.get(
                    f"https://api.github.com/repos/{req[0]}/{req[1]}/{'zipball' if system() == 'Windows' else 'tarball'}/{branch}",
                    stream=True,
                )

            except Exception as e:
                print(f"An unexpected error occurred: {e}")

            if system() == "Windows":
                with ZipFile(BytesIO(response.content)) as z:
                    z.extractall(dependency_path)

            if system() == "Linux":
                with tarfile.open(BytesIO(response.content), "r:gz") as tar_ref:
                    tar_ref.extractall(dependency_path)

            renamed_dir = os.path.join(dependency_path, branch)
            print(f"Installed: {os.listdir(dependency_path)[0]}")
            os.rename(
                os.path.join(dependency_path, os.listdir(dependency_path)[0]),
                renamed_dir,
            )
            libs = get_requirements(renamed_dir)
            if libs:
                download_requirements(libs)


def get_requirements(dir) -> list | None:
    with open(os.path.join(dir, "pulse.toml")) as f:
        requirements = toml.load(f)

    try:
        requirements["requirements"]["live"]
        print("Found requirements!\nInstalling..")
    except:
        return None

    else:
        return requirements["requirements"]["live"]
