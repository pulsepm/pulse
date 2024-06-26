import os
import shutil

import click

import pulse.core.git.git_get as git_get
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
    for i, release in enumerate(git_get.get_github_runtime_releases(), start=1):
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
