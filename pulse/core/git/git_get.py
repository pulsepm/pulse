import requests
from typing import Literal
import os
import toml


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


def get_github_repo(
    owner: str,
    repo: str,
    syntax: str,
    type: Literal["branch", "commit", "version"] = None,
) -> list:
    try:
        if type == "branch" or type == "commit":
            url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{syntax}"

        if type == "version":
            url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/tags/{syntax}"

        if not type:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents"

        response = requests.get(url)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    else:
        if type == "version":
            tmp_ = response.json()
            return get_github_repo(owner, repo, tmp_["object"]["sha"], type="commit")

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


def get_requirements(dir) -> list | None:
    with open(os.path.join(dir, "pulse.toml")) as f:
        requirements = toml.load(f)

    try:
        requirements["requirements"]["live"]
    except:
        return None

    else:
        return requirements["requirements"]["live"]