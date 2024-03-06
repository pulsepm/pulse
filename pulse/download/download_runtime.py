import click
import os
import shutil
import pulse.core.git.git as git
from pulse.core.core_dir import RUNTIME_PATH
from .download_asset import get_asset
runtimes_dict: dict[int, str] = {}

def get_runtime() -> None:
    """
    Prompts user to install specified runtime

    Returns:
        None
    """
    click.echo("Select the version of the runtime you would like to install.")
    for i, release in enumerate(git.get_github_runtime_releases(), start=1):
        runtimes_dict[i] = release['name']
        click.echo(f"{i}. {release['name']}")

    runtime_choice = click.prompt("Enter your choice", type=click.IntRange(1, i))
    continue_confirm = click.confirm("Do you want to continue?")
    if not continue_confirm:
        return click.echo("Cancelled.")

    runtime_path = os.path.join(RUNTIME_PATH, runtimes_dict[runtime_choice])
    if not os.path.exists(runtime_path):
        click.echo("Runtime is not found in the cache, it will be downloaded.")
        click.echo(f"Downloading runtime ({runtimes_dict[runtime_choice]})..")
        get_asset("runtime", runtimes_dict[runtime_choice])

    pods_runtime = os.path.join(os.getcwd(), ".pods/runtime")
    shutil.copytree(os.path.join(RUNTIME_PATH, runtimes_dict[runtime_choice]), pods_runtime)
