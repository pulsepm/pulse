from typing import Union, Literal
import git
import os
import tomli
from ..core.core_dir import safe_open, CONFIG_FILE

import requests


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

    # STROKE THIS!!!
    if not valid_username(username=username):
        print("Not valid username")
        return

    if not valid_token(token=access_token):
        print("Not valid token")
        return

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
            return

        local_repo = git.Repo.init(os.getcwd())

        origin_url = f"https://github.com/{username}/{repository_name}.git"
        origin = local_repo.create_remote('origin', url=origin_url)

        print(f"Local repository initialized at: {os.getcwd()}")
        print(f"Remote origin set to: {origin_url}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def valid_token(token: str) -> bool:
    url = "https://api.github.com/user"
    headers = {"Authorization": f"token {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return True
    else:
        return False


def valid_username(username: str) -> bool:
    url = f"https://api.github.com/users/{username}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    

def get_github_repo(
    author: str, repo: str, syntax: str, syntax_type: Literal["@", ":", "#"]
) -> list | bool:
    if syntax_type == "@" or syntax_type == "#":
        url = f"https://api.github.com/repos/{author}/{repo}/git/trees/{syntax}"

    if syntax_type == ":":
        url = f"https://api.github.com/repos/{author}/{repo}/contents?ref={syntax}"

    if not syntax_type:
        url = f"https://api.github.com/repos/{author}/{repo}/contents"

    with safe_open(CONFIG_FILE, 'rb') as toml_file:
        token_data = tomli.load(toml_file)
        token = token_data["token"]

    headers = {
        "Authorization": f"token {token}"
    }

    response = requests.get(url, headers=headers)
    if not response.ok:
        return response

    return response.json()


def default_branch(package: list[str]) -> str | int:
    with safe_open(CONFIG_FILE, 'rb') as token_file:
        token_data = tomli.load(token_file)
        token = token_data["token"]
    
    url = f"https://api.github.com/repos/{package[0]}/{package[1]}"
    headers = {
        "Authorization": f"token {token}"
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        print(response.json())
        return response.json()

    return response.json()["default_branch"]


def get_latest_tag(author: str, repo: str, ref: str | None = None) -> str | None:
    """
    Get the latest tag for a specific branch or commit.
    
    Args:
        author (str): Repository owner
        repo (str): Repository name
        ref (str, optional): Branch name or commit SHA. If None, gets latest tag from default branch
    
    Returns:
        str | None: The tag name if found, None if no tags exist
    """
    with safe_open(CONFIG_FILE, 'rb') as toml_file:
        token_data = tomli.load(toml_file)
        token = token_data["token"]

    headers = {"Authorization": f"token {token}"}
    
    tags_url = f"https://api.github.com/repos/{author}/{repo}/tags"
    tags_response = requests.get(tags_url, headers=headers)
    
    if not tags_response.ok or not tags_response.json():
        return None
    
    if not ref:
        return tags_response.json()[0]["name"]
    
    commit_url = f"https://api.github.com/repos/{author}/{repo}/commits/{ref}"
    commit_response = requests.get(commit_url, headers=headers)
    
    if not commit_response.ok:
        return None
    
    target_sha = commit_response.json()["sha"]
    
    for tag in tags_response.json():
        if tag["commit"]["sha"] == target_sha:
            return tag["name"]
    
    return None


def get_release_assets(author: str, repo: str, tag: str) -> list | None:
    """
    Get all assets for a specific release.
    
    Args:
        author (str): Repository owner
        repo (str): Repository name
        tag (str): Release tag
        
    Returns:
        list | None: List of asset objects or None if not found
    """
    with safe_open(CONFIG_FILE, 'rb') as toml_file:
        token_data = tomli.load(toml_file)
        token = token_data["token"]

    headers = {"Authorization": f"token {token}"}
    
    url = f"https://api.github.com/repos/{author}/{repo}/releases/tags/{tag}"
    response = requests.get(url, headers=headers)
    
    if not response.ok:
        return None
        
    release_data = response.json()
    return release_data.get("assets", [])

