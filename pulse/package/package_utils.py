import click
import tomli
import tomli_w
import os

def get_package_type(package: str) -> str | None:
    return "==" if "==" in package else ":" if ":" in package else "@"


def echo_retrieve_fail(package: list, code: int) -> str:
    return click.echo(f"Failed to retrieve package: {package[0]}/{package[1]} (code: {code})!")


def write_requirements(owner: str, repo: str, sign: str, syntax: str) -> None:
    package_name: str = f"{owner}/{repo}{sign}{syntax}"
    with open(os.path.join(os.getcwd(), "pulse.toml"), "rb") as file:
        data = tomli.load(file)

    if "requirements" not in data:
        data["requirements"] = {"live": []}

    if package_name not in data["requirements"]["live"]:
        data["requirements"]["live"].append(package_name)
        with open(os.path.join(os.getcwd(), "pulse.toml"), "wb") as file:
            tomli_w.dump(data, file, multiline_strings=True)