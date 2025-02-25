from typing import Union, Literal
import git
import os
import tomli
from ..core.core_dir import safe_open
from ..user import User
from github import Github
import logging
import requests
from pathlib import Path

usr = User()

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

    headers = {
        "Authorization": f"token {usr.git_token}"
    }

    response = requests.get(url, headers=headers)
    if not response.ok:
        return response

    return response.json()


def default_branch(package: list[str]) -> str | int:
    
    url = f"https://api.github.com/repos/{package[0]}/{package[1]}"
    headers = {
        "Authorization": f"token {usr.git_token}"
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
    g = Github(usr.git_token)
    try:
        repository = g.get_repo(f"{author}/{repo}")
        tags = list(repository.get_tags())
        
        if not tags:
            return None
            
        if not ref:
            # Just get the latest tag by date
            sorted_tags = sorted(tags, key=lambda x: x.commit.commit.author.date, reverse=True)
            return sorted_tags[0].name
        
        # Get the specific commit without fetching history
        target_commit = repository.get_commit(ref)
        target_sha = target_commit.sha
        
        # First try exact match
        for tag in tags:
            if tag.commit.sha == target_sha:
                return tag.name
        
        # If no exact match, get the latest tag that's reachable from this commit
        # Sort tags by date first to try newest ones first
        sorted_tags = sorted(tags, key=lambda x: x.commit.commit.author.date, reverse=True)
        for tag in sorted_tags:
            try:
                # Check if tag commit is an ancestor of target commit
                comparison = repository.compare(tag.commit.sha, target_sha)
                if comparison.ahead_by == 0:
                    return tag.name
            except:
                continue
                
        return None
        
    except Exception as e:
        logging.error(f"Error getting latest tag: {e}")
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

    headers = {"Authorization": f"token {usr.git_token}"}
    
    url = f"https://api.github.com/repos/{author}/{repo}/releases/tags/{tag}"
    response = requests.get(url, headers=headers)
    
    if not response.ok:
        return None
        
    release_data = response.json()
    return release_data.get("assets", [])


def download_file_from_github(repo_owner: str, repo_name: str, file_path: str, target_dir: str | Path) -> bool:
    """
    Download a specific file from GitHub repository's default branch.
    
    Args:
        repo_owner (str): Repository owner
        repo_name (str): Repository name
        file_path (str): Path to the file in the repository
        target_dir (str|Path): Directory where to save the file
        
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        g = Github(usr.git_token)
        repo = g.get_repo(f"{repo_owner}/{repo_name}")
        default_branch = repo.default_branch
        
        content = repo.get_contents(file_path, ref=default_branch)
        if isinstance(content, list):
            logging.error(f"{file_path} is a directory, skipping")
            return False
            
        save_path = Path(target_dir) / file_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(content.decoded_content)
            
        logging.info(f"Successfully downloaded {file_path} from default branch to {save_path}")
        return True
        
    except Exception as e:
        logging.warning(f"Failed to download {file_path}: {e}")
        return False


def check_files_github(repo_owner, repo_name, ref, files_to_check=['pulse.toml', 'pawn.json']):
    """
    Check for config files in repository.
    Prioritizes pulse.toml over pawn.json.
    
    Args:
        repo_owner (str): Repository owner
        repo_name (str): Repository name
        ref (str): Branch, tag or commit to check
        files_to_check (list): List of files to check, ordered by priority
        
    Returns:
        tuple: (dict of file existence, file that was found)
    """

    g = Github(usr.git_token)  
    repo = g.get_repo(f"{repo_owner}/{repo_name}")
    default_branch = repo.default_branch
    
    results = {file: False for file in files_to_check}
    found_file = None
    
    logging.info(f"Checking files in {repo_owner}/{repo_name} at ref: {ref}")
    
    # First check files in specified ref
    for file in files_to_check:
        try:
            repo.get_contents(file, ref=ref)
            results[file] = True
            found_file = file
            logging.info(f"Found {file}")
            return results, found_file
        except Exception:
            logging.warning(f"Missing {file}")
    
    # If no files found, try default branch
    if ref != default_branch:
        logging.info(f"No config files found in {ref}, trying default branch: {default_branch}")
        for file in files_to_check:
            try:
                repo.get_contents(file, ref=default_branch)
                results[file] = True
                found_file = file
                logging.info(f"Found {file} in default branch")
                return results, found_file
                
            except Exception:
                logging.warning(f"Missing {file} in default branch")
                
    return results, found_file