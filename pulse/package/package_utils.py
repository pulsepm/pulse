import re
import click
import tomli
import tomli_w
import os
import stat
from typing import Callable, Literal
from pulse.core.core_dir import PACKAGE_PATH


def get_package_syntax(package: str) -> str | None:
    return "==" if "==" in package else ":" if ":" in package else "@"


def echo_retrieve_fail(package: list, code: int) -> str:
    return click.echo(
        f"Failed to retrieve package: {package[0]}/{package[1]} (code: {code})!"
    )


def write_requirements(owner: str, repo: str, sign: str, syntax: str) -> None:
    package_name: str = f"{owner}/{repo}{sign}{syntax}"
    toml_path = os.path.join(os.getcwd(), "pulse.toml")

    if not os.path.exists(toml_path):
        tmp_file = open(toml_path, mode="w")
        tmp_file.close()

    with open(toml_path, "rb") as file:
        data = tomli.load(file)

    if "requirements" not in data:
        data["requirements"] = {"live": []}

    if package_name not in data["requirements"]["live"]:
        data["requirements"]["live"].append(package_name)
        with open(toml_path, "wb") as file:
            tomli_w.dump(data, file, multiline_strings=True)


def remove_requirements(owner: str, repo: str, sign: str, syntax: str) -> None:
    package_name: str = f"{owner}/{repo}{sign}{syntax}"
    toml_path = os.path.join(os.getcwd(), "pulse.toml")
    with open(toml_path, "rb") as file:
        data = tomli.load(file)

    if package_name in data["requirements"]["live"]:
        data["requirements"]["live"].remove(package_name)
        with open(toml_path, "wb") as file:
            tomli_w.dump(data, file, multiline_strings=True)


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


def on_rm_error(function: Callable, path, info):
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def get_resource_file(plugin: str) -> str:
    file = re.search(r'[^\\/]*$', plugin)
    return file.group(0) if file else plugin
