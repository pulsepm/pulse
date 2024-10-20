from platform import system
import os
import tomli
import json
from typing import Literal
from ...core.core_dir import PACKAGE_PATH

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


def get_package_syntax(package: str) -> str | None:
    return "#" if "#" in package else ":" if ":" in package else "@"


def get_package_type(git_repo: list | dict) -> Literal["pulse", "sampctl", False]:
    if isinstance(git_repo, dict):
        git_repo = list(git_repo.values())

    for file in git_repo:
        try:
            file["path"]
        except:
            if isinstance(file, list):
                for i in file:
                    if "pulse.toml" in i["path"]:
                        return "pulse"

                    if "pawn.json" in i["path"]:
                        return "sampctl"

        else:
            if "pulse.toml" in file["path"]:
                return "pulse"

            if "pawn.json" in file["path"]:
                return "sampctl"

    return False


def get_local_package_type(owner: str, repo: str, version: str) -> Literal["pulse", "sampctl", False]:
    local_path = os.path.join(PACKAGE_PATH, owner, repo, version)
    if os.path.exists(os.path.join(local_path, "pulse.toml")):
        return "pulse"

    if os.path.exists(os.path.join(local_path, "pawn.json")):
        return "sampctl"

    return False


def echo_retrieve_fail(package: list, code: int) -> str:
    return click.echo(
        f"Failed to retrieve package: {package[0]}/{package[1]} (code: {code})!"
    )
