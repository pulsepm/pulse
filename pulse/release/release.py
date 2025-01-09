import click
import os
import tomli
import pulse.stroke.stroke_dump as stroke
import logging

from typing import Any

from ..core.core_dir import CONFIG_PATH
from ..git.git_release import publish_release

@click.command
@click.option("--pre", "-p", type=bool, required=False, is_flag=True, default=False)
def release(pre: bool):
    r_data: dict[str, Any] = {}
    user_data: dict[str, Any] = {}
    project_data: dict[str, Any] = {}
    if not os.path.isfile(os.path.join(os.getcwd(), "package.rel")):
        logging.fatal("Fatal error occurred -> Invalid release file. Exit code: 51")
        stroke.dump(51)
        return

    try:
        with open(os.path.join(os.getcwd(), "package.rel"), "rb") as r:
            r_data = tomli.load(r)

        with open(os.path.join(os.getcwd(), "pulse.toml"), "rb") as p:
            project_data = tomli.load(p)

        with open(os.path.join(CONFIG_PATH, "pulseconfig.toml"), "rb") as c:
            user_data = tomli.load(c)

        files_to_attach: list[str] = []
        if "rel_windows" in r_data:
            files_to_attach.append(r_data["rel_windows"])
        if "rel_linux" in r_data:
            files_to_attach.append(r_data["rel_linux"])

        tag_message: str = click.prompt("Tag message")
        release_name: str = click.prompt("Input your release title")
        release_message: str = click.prompt("Input your release information")

        repo_name: str = (
            f"{project_data['project']['publisher']}/{project_data['project']['repo']}"  # Format: "owner/repo"
        )

        publish_release(
            os.path.join(os.getcwd(), ".git"),
            r_data["version"],
            tag_message,
            release_name,
            release_message,
            files_to_attach,
            user_data["token"],
            repo_name,
            pre
        )

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
