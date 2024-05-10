import click
import tomli
import tomli_w
import os
from typing import Literal


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

    type: str = None
    for file in git_repo:
        try:
            file["path"]
        except:
            if isinstance(file, list):
                for i in file:
                    if "pulse.toml" in i["path"]:
                        type = "pulse"
                        break

                    if "pawn.json" in i["path"]:
                        type = "sampctl"
                        break

        else:
            if "pulse.toml" in file["path"]:
                type = "pulse"
                break

            if "pawn.json" in file["path"]:
                type = "sampctl"
                break

    return type if type else False


# def get_local_package_type(owner: str, repo: str, version: str) -> Literal["pulse", "sampctl", False]:
#     with open()
