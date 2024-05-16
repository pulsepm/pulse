import requests
from typing import Literal
import os
import tomli
import logging
import pulse.stroke.stroke as stroke


def get_github_compiler_releases() -> list:
    """
    Retrieves a list of compiler releases from a GitHub repository.

    Returns:
        list: A list of compiler releases available in the GitHub repository.
    """
    try:
        response = requests.get("https://api.github.com/repos/pulsepm/compiler/tags")

    except Exception as e:
        logging.fatal(f"Failed to get compiler releases: {e}" )
        stroke.dump(4)

    else:
        return response.json()


def get_github_runtime_releases() -> list:
    """
    Retrieves a list of runtime releases from a GitHub repository.

    Returns:
        list: A list of runtime releases available in the GitHub repository.
    """

    try:
        response = requests.get(
            "https://api.github.com/repos/openmultiplayer/open.mp/tags"
        )

    except Exception as e:
        logging.fatal(f"Failed to get runtime releases: {e}" )
        stroke.dump(4)

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


def default_branch(package: list[str]) -> str | int:
    url = f"https://api.github.com/repos/{package[0]}/{package[1]}"
    response = requests.get(url)
    if not response.ok:
        return response.status_code

    return response.json()["default_branch"]


def get_requirements(directory, package_type: Literal["pulse", "sampctl"]) -> list | None:
    try:
        with open(os.path.join(directory, "pulse.toml" if package_type == "pulse" else "pawn.json"), mode="rb" if package_type == "pulse" else "r") as f:
            if package_type == "pulse":
                requirements = tomli.load(f)
            else:
                requirements = json.load(f)
    except:
        return None

    try:
        requirements["requirements"]["live"] if package_type == "pulse" else requirements["dependencies"]
    except:
        return None

    else:
        return requirements["requirements"]["live"] if package_type == "pulse" else requirements["dependencies"]


def get_package_resources(directory, package_type: Literal["pulse", "sampctl"]) -> tuple[str] | None:
    try:
        with open(os.path.join(directory, "pulse.toml" if package_type == "pulse" else "pawn.json"), mode="rb" if package_type == "pulse" else "r") as f:
            if package_type == "pulse":
                resource = tomli.load(f)
            else:
                resource = json.load(f)

        if package_type == "pulse":
            return (resource["project"]["publisher"], resource["project"]["repo"], resource["resource"][system().lower()]["name"])

        else:
            index: int = 0 if resource["resources"][0]["platform"] == system().lower() else 1
            return (resource["user"], resource["repo"], resource["resources"][index]["name"])

    except:
        return None


def get_resource_plugins(directory, package_type: Literal["pulse", "sampctl"]) -> list[str] | None:
    try:
        with open(os.path.join(directory, "pulse.toml" if package_type == "pulse" else "pawn.json"), mode="rb" if package_type == "pulse" else "r") as f:
            if package_type == "pulse":
                resource = tomli.load(f)
            else:
                resource = json.load(f)

        if package_type == "pulse":
            return resource["resource"][system().lower()]["plugins"]

        else:
            index: int = 0 if resource["resources"][0]["platform"] == system().lower() else 1
            return resource["resources"][index]["plugins"]

    except:
        return None
