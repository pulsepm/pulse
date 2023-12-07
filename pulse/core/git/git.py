import git

def clone_github_repo(repo_url, destination_folder):
    try:
        git.Repo.clone_from(repo_url, destination_folder, force=True)
        print(f"Repository cloned successfully to {destination_folder}")
    except git.GitCommandError as e:
        print(f"Error cloning repository: {e}")

def download_and_unzip_openmp(url, downloaded_name):
    target_folder = os.getcwd()
    # Download the ZIP file
    response = requests.get(url)
    
    if response.status_code == 200:
        zip_file_path = os.path.join(target_folder, downloaded_name)

        with open(zip_file_path, 'wb') as zip_file:
            zip_file.write(response.content)

        # Unzip the downloaded folder if windows
        if str(downloaded_name).endswith('.zip'):
            with ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
        elif str(downloaded_name).endswith('.tar.gz'):
            with tarfile.open(file_path, 'r:gz') as tar_ref:
                tar_ref.extractall(target_folder) 
        else:
            print(f"Unsupported operating system: {platform.system()}")
            return

        # Remove the downloaded ZIP file if needed
        os.remove(zip_file_path)
        print(f"Folder downloaded and extracted to: {target_folder}")
    else:
        print(f"Failed to download the folder. HTTP Status Code: {response.status_code}")
