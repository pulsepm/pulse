import requests
from typing import Literal
import os
import tomli
import json
import pulse.package.package_utils as package_utils


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
    author: str, repo: str, syntax: str, type: Literal["@", ":", "=="]
) -> list | bool:
    if type == "@" or type == ":":
        url = f"https://api.github.com/repos/{author}/{repo}/git/trees/{syntax}"

    if type == "==":
        url = f"https://api.github.com/repos/{author}/{repo}/git/refs/tags/{syntax}"

    if not type:
        url = f"https://api.github.com/repos/{author}/{repo}/contents"

    response = requests.get(url)
    if not response.ok:
        return False

    if type == "==":
        tmp_ = response.json()
        return get_github_repo(author, repo, tmp_["object"]["sha"], ":")

    return response.json()


def default_branch(package: list) -> str | int:
    url = f"https://api.github.com/repos/{package[0]}/{package[1]}"
    response = requests.get(url)
    if not response.ok:
        return response.status_code

    return response.json()["default_branch"]


def get_requirements(directory, package_type: Literal["sampctl", "pulse"]) -> list | None:
    if package_type == "pulse":
        try:
            with open(os.path.join(directory, "pulse.toml"), mode="rb") as f:
                requirements = tomli.load(f)
        except:
            return None

        try:
            requirements["requirements"]["live"]
        except:
            return None

        else:
            return requirements["requirements"]["live"]

    if package_type == "sampctl":
        try:
            with open(os.path.join(directory, "pawn.json"), mode="r") as f:
                requirements = json.load(f)
        except:
            return None

        try:
            requirements["dependencies"]
        except:
            return None

        else:
            return requirements["dependencies"]
