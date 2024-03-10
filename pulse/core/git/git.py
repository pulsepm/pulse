from typing import Union

import requests


def check_github_repo_exists(username: str, repo_name: str) -> Union[bool, None]:
    """
    Checks if a GitHub repository exists for the given username and repository name.

    Args:
        username (str): The username of the repository owner.
        repo_name (str): The name of the repository.

    Returns:
        Union[bool, None]: Returns True if the repository exists, False if it does not exist, or None if there was an issue checking the repository.
    """
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    response = requests.get(url)

    if response.status_code == 200:
        print(f"The repository {username}/{repo_name} exists.")
        return True
    elif response.status_code == 404:
        print(f"The repository {username}/{repo_name} does not exist.")
        return False
    else:
        print(f"Failed to check the repository. Status code: {response.status_code}")
        return None


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
        create_repo_url = "https://api.github.com/user/repos"
        headers = {"Authorization": f"token {access_token}"}
        data = {"name": repository_name, "auto_init": False, "private": False}

        response = requests.post(create_repo_url, headers=headers, json=data)

        if response.status_code == 201:
            print(f"Repository '{repository_name}' created on GitHub successfully.")
            print(
                f"You can visit it via: https://github.com/{username}/{repository_name}"
            )
        else:
            print(
                f"Failed to create repository on GitHub. Status code: {response.status_code}, Message: {response.text}"
            )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

