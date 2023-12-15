import git
import requests
import os
from zipfile import ZipFile
import tarfile
import shutil
import platform

def clone_github_repo(repo_url, destination_folder):
    try:
        git.Repo.clone_from(repo_url, destination_folder, force=True)
        print(f"Repository cloned successfully to {destination_folder}")
    except git.GitCommandError as e:
        print(f"Error cloning repository: {e}")

def download_and_unzip_github_release(owner, repo, tag, asset_name):
    target_folder = os.getcwd()

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
        system = platform.system()
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
        server_folder = os.path.join(target_folder, 'Server')
        components = os.path.join(server_folder, 'components')
        config_json = os.path.join(server_folder, 'config.json')
        server_exe = os.path.join(server_folder, 'omp-server.exe' if system == "Windows" else 'omp-server')
        if system == "Windows":
            server_pdb = os.path.join(server_folder, 'omp-server.pdb')
            shutil.move(server_pdb, target_folder)
        
        shutil.move(components, target_folder)
        shutil.move(server_exe, target_folder)
        shutil.move(config_json, target_folder)

        shutil.rmtree(server_folder)
    else:
        print(f"Failed to download the asset. HTTP Status Code: {response.status_code}")


def check_github_repo_exists(username, repo_name):
    url = f'https://api.github.com/repos/{username}/{repo_name}'
    response = requests.get(url)

    if response.status_code == 200:
        print(f"The repository {username}/{repo_name} exists.")
    elif response.status_code == 404:
        print(f"The repository {username}/{repo_name} does not exist.")
    else:
        print(f"Failed to check the repository. Status code: {response.status_code}")
