import os
import platform

import click

import pulse.git.git_download as git_download
from pulse.core.core_dir import COMPILER_PATH, RUNTIME_PATH


def get_asset(type: str, version: str) -> None:
    """
    Downloads particular asset specified by version and type.

    Args:
        type (str): The type of files to download.
        version (str):
    """
    system = platform.system()
    if type == "runtime":
        git_download.download_and_unzip_github_release(
            "openmultiplayer",
            "open.mp",
            version,
            (
                "open.mp-win-x86.zip"
                if system == "Windows"
                else "open.mp-linux-x86.tar.gz"
            ),
            RUNTIME_PATH,
        )

        server_folder = os.path.join(RUNTIME_PATH, version)
        os.rename(os.path.join(RUNTIME_PATH, "Server"), server_folder)

    elif type == "compiler":
        git_download.download_and_unzip_github_release(
            "pulsepm",
            "compiler",
            version,
            (
                f"pawnc-win-{version}.zip"
                if system == "Windows"
                else f"pawnc-linux-{version}.tar.gz"
            ),
            os.path.join(COMPILER_PATH, version),
        )

    else:
        click.echo("Invalid type.")
