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
    package: list,
    type: Literal["@", ":", "=="]
) -> list | int:
    if type == "@" or type == ":":
        url = f"https://api.github.com/repos/{package[0]}/{package[1]}/git/trees/{package[2]}"

    if type == "==":
        url = f"https://api.github.com/repos/{package[0]}/{package[1]}/git/refs/tags/{package[2]}"

    if not type:
        url = f"https://api.github.com/repos/{package[0]}/{package[1]}/contents"

    response = requests.get(url)
    if not response.ok:
        return False

    if type == "==":
        tmp_ = response.json()
        return get_github_repo(package[0], package[1], syntax=tmp_["object"]["sha"])

    return response.json()


def default_branch(package: list) -> str | int:
    url = f"https://api.github.com/repos/{package[0]}/{package[1]}"
    response = requests.get(url)
    if not response.ok:
        return response.status_code

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
