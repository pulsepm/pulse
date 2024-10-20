import os
import shutil

import click
from pulse.core.core_dir import RUNTIME_PATH, PODS_PATH

from .download_asset import get_asset

runtimes_dict: dict[int, str] = {}


def get_runtime(isolate: bool = True) -> None:
    """
    Prompts user to install specified runtime

    Returns:
        None
    """
    click.echo("Select the runtime you would like to use.")
    for i, release in enumerate(get_github_runtime_releases(), start=1):
        runtimes_dict[i] = release["name"]
        click.echo(f"{i}. {release['name']}")

    runtime_choice = click.prompt("Enter your choice", type=click.IntRange(1, i))

    runtime_path = os.path.join(RUNTIME_PATH, runtimes_dict[runtime_choice])
    if not os.path.exists(runtime_path):
        click.echo("Runtime is not found in the cache, it will be downloaded.")
        click.echo(f"Downloading runtime ({runtimes_dict[runtime_choice]})..")
        get_asset("runtime", runtimes_dict[runtime_choice])

    if isolate:
        pods_runtime = os.path.join(os.getcwd(), PODS_PATH, "runtime")
        shutil.copytree(
            os.path.join(RUNTIME_PATH, runtimes_dict[runtime_choice]), pods_runtime
        )

    else:
        pass  # Handle adding those to pulse.toml

    return runtimes_dict[runtime_choice]


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
