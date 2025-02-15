import os
import tarfile
from zipfile import ZipFile
import requests
from github import Github
import logging
from ..core.core_dir import safe_open, CONFIG_FILE
import tomli


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
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
    response = requests.get(api_url)

    if response.status_code != 200:
        print(
            f"Failed to get release information. HTTP Status Code: {response.status_code}"
        )
        return

    release_info = response.json()

    asset_url = None
    for asset in release_info.get("assets", []):
        if asset["name"] == asset_name:
            asset_url = asset["browser_download_url"]
            break

    if asset_url is None:
        print(f"Asset '{asset_name}' not found in the release.")
        return

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
    try:
        with safe_open(CONFIG_FILE, 'rb') as toml_file:
            token_data = tomli.load(toml_file)
            token = token_data["token"]

        g = Github(token)
        repository = g.get_repo(f"{owner}/{repo}")
        
        try:
            release = repository.get_release(tag)
        except Exception:
            logging.error(f"Failed to get release information for tag: {tag}")
            return None

        asset = None
        for a in release.get_assets():
            if a.name == asset_name:
                asset = a
                break

        if asset is None:
            logging.error(f"Asset '{asset_name}' not found in the release")
            return None

        try:
            os.makedirs(target_folder, exist_ok=True)
            asset_path = os.path.join(target_folder, asset_name)
            
            headers = {
                "Accept": "application/octet-stream",
                "Authorization": f"token {token}"
            }
            
            response = requests.get(
                asset.browser_download_url,
                headers=headers,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                with open(asset_path, 'wb') as f:
                    f.write(response.content)
                logging.info("Asset download successful")
                return asset_path
            else:
                logging.error(f"Failed to download asset. Status code: {response.status_code}")
                return None
            
        except Exception as e:
            logging.error(f"Failed to download asset: {e}")
            return None

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None

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