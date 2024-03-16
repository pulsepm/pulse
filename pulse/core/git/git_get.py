import requests
from typing import Union

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
        response = requests.get(
            "https://api.github.com/repos/openmultiplayer/open.mp/tags"
        )

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    else:
        return response.json()


def get_github_repo(owner: str, repo: str, branch: str = None, commit: str = None, version: str = None) -> Union[dict, list]:
    try:
        if branch or commit:
            url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch if branch else commit}"

        if version:
            url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/tags/{version}"

        else:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents"

        response = requests.get(url)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    else:
        if version:
            return get_github_repo(owner, repo, commit=response.json()["object"]["url"])

        else:
            return response.json()


def default_branch(owner: str, repo: str) -> str:
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    else:
        return response.json()["default_branch"]