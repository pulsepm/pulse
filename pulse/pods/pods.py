import os
import shutil

import click

import pulse.download.download as download

from pulse.core.core_dir import PODS_PATH


@click.command
def pods() -> None:
    """
    Initialize project isolation.

    """
    if not os.path.exists(os.path.join(os.getcwd(), 'pulse.toml')):
        return print("This is not a pulse package!")

    if os.path.exists(PODS_PATH):
        click.echo("Pulse pods have already been initialized!")
        click.echo("Select an action with the pulse pods:")
        click.echo("1. Delete\n2. Modify\n3. Cancel")
        choice = click.prompt("Enter your choice", type=click.IntRange(1, 3))
        if choice == 1:
            if not click.confirm("Are you sure?"):
                return click.echo("Canceled!")

            shutil.rmtree(PODS_PATH)
            return click.echo("Pulse pods was successfully deleted!")

        if choice == 2:
            if not click.confirm(
                "Are you sure? This action will delete the current runtimes' files"
            ):
                return click.echo("Canceled!")

            shutil.rmtree(os.path.join(PODS_PATH, "runtime"))
            download.get_runtime()

            return click.echo("Pulse pods has been successfully modified!")

        if choice == 3:
            return click.echo("Canceled!")

    download.get_runtime()
    return click.echo("Pulse pods has been successfully initialized!")
