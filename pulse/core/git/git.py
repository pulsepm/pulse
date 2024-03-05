import git
import requests
import os
import platform
import subprocess
from zipfile import ZipFile
import tarfile


# Implement URL type
def clone_github_repo(repo_url, destination_folder: str, no_git=True) -> None:
    """
    Clones a GitHub repository to a specified destination folder and optionally removes the .git directory.

    Args:
        repo_url (str): The URL of the GitHub repository to clone.
        destination_folder (str): The local path where the repository will be cloned.
        no_git (bool, optional): A flag indicating whether to remove the .git directory after cloning. Default is True.

    Returns:
        None

    Raises:
        git.GitCommandError: If an error occurs during the cloning process.
    """
    try:
        git.Repo.clone_from(repo_url, destination_folder)

        if no_git is True:
            path = os.path.join(destination_folder, '.git')
            if platform.system() == "Windows":
                subprocess.run(
                    ["cmd", "/c", "rd", "/s", "/q", path], check=True
                )
            else:
                subprocess.run(["rm", "-rf", path], check=True)

        print(f"Repository cloned successfully to {destination_folder}")
    except git.GitCommandError as e:
        print(f"Error cloning repository: {e}")


def download_and_unzip_github_release(owner: str, repo: str, tag: str, asset_name: str, target_folder: str) -> None:
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
        print(f"Failed to get release information. HTTP Status Code: {response.status_code}")
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
        print('Asset download successful')
        os.makedirs(target_folder, exist_ok=True)
        asset_path = os.path.join(target_folder, asset_name)

        with open(asset_path, 'wb') as asset_file:
            asset_file.write(response.content)

        # Unzip the downloaded asset if it is a zip file
        if str(asset_name).endswith('.zip'):
            with ZipFile(asset_path, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
        elif str(asset_name).endswith('.tar.gz'):
            with tarfile.open(asset_path, 'r:gz') as tar_ref:
                tar_ref.extractall(target_folder)
        else:
            print(f"Unsupported asset type: {asset_name}")
            return

        # Remove the downloaded asset file if needed
        os.remove(asset_path)
        print(f"Asset downloaded and extracted to: {target_folder}")

    else:
        print(f"Failed to download the asset. HTTP Status Code: {response.status_code}")

# Refactor this so it returns boolean
def check_github_repo_exists(username: str, repo_name: str) -> None:
    url = f'https://api.github.com/repos/{username}/{repo_name}'
    response = requests.get(url)

    if response.status_code == 200:
        print(f"The repository {username}/{repo_name} exists.")
    elif response.status_code == 404:
        print(f"The repository {username}/{repo_name} does not exist.")
    else:
        print(f"Failed to check the repository. Status code: {response.status_code}")


def create_repository(username: str, repository_name: str, access_token: str) -> None:
    """
    Creates a new GitHub repository for a specified user.

    Args:
        username (str): The username of the owner who will own the new repository.
        repository_name (str): The name of the new repository to be created.
        access_token (str): The access token with the required permissions to create repositories.

    Returns:
        None
    """
    try:
        create_repo_url = 'https://api.github.com/user/repos'
        headers = {'Authorization': f"token {access_token}"}
        data = {'name': repository_name, 'auto_init': False, 'private': False}

        response = requests.post(create_repo_url, headers=headers, json=data)

        if response.status_code == 201:
            print(f"Repository '{repository_name}' created on GitHub successfully.")
            print(f"You can visit it via: https://github.com/{username}/{repository_name}")
        else:
            print(f"Failed to create repository on GitHub. Status code: {response.status_code}, Message: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def get_github_compiler_releases() -> list:
    """
    Retrieves a list of compiler releases from a GitHub repository.

    Returns:
        list: A list of compiler releases available in the GitHub repository.
    """
    try:
        response = requests.get("https://api.github.com/repos/pulsepm/compiler/tags")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    else:
        return response.json()


def get_github_runtime_releases() -> list:
    """
    Retrieves a list of compiler releases from a GitHub repository.

    Returns:
        list: A list of compiler releases available in the GitHub repository.
    """

    try:
        response = requests.get("https://api.github.com/repos/openmultiplayer/open.mp/tags")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    else:
        return response.json()
