import os
import platform
import subprocess

import git

from pulse.core.core_url import Url


def clone_github_repo(repo_url: Url, destination_folder: str, no_git=True) -> None:
    """
    Clones a GitHub repository to a specified destination folder and optionally removes the .git directory.

    Args:
        repo_url (Url): The URL of the GitHub repository to clone.
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
            path = os.path.join(destination_folder, ".git")
            if platform.system() == "Windows":
                subprocess.run(["cmd", "/c", "rd", "/s", "/q", path], check=True)
            else:
                subprocess.run(["rm", "-rf", path], check=True)

        print(f"Repository cloned successfully to {destination_folder}")
    except git.GitCommandError as e:
        print(f"Error cloning repository: {e}")
