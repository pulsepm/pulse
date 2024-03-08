import click
import os
import shutil
import pulse.download.download as download


@click.command
def pods() -> None:
    """
    Initialize project isolation.

    """
    if not os.path.exists(os.path.join(os.getcwd(), "pulse.toml")):
        return print("This is not a pulse package!")

    if os.path.exists(os.path.join(os.getcwd(), ".pods")):
        click.echo("Pulse pods have already been initialized!")
        click.echo("Select an action with the pulse pods:")
        click.echo("1. Delete\n2. Modify\n3. Cancel")
        choice = click.prompt("Enter your choice", type=click.IntRange(1, 3))
        if choice == 1:
            if not click.confirm("Are you sure?"):
                return click.echo("Canceled!")

            shutil.rmtree(os.path.join(os.getcwd(), ".pods"))
            return click.echo("Pulse pods was successfully deleted!")

        if choice == 2:
            if not click.confirm(
                "Are you sure? This action will delete the current runtimes/compiler files"
            ):
                return click.echo("Canceled!")

            click.echo("Select what needs to be modified:")
            click.echo("1. Compiler\n2. Runtime")
            choice_mod = click.prompt("Enter your choice", type=click.IntRange(1, 2))
            if choice_mod == 1:
                shutil.rmtree(os.path.join(os.getcwd(), ".pods/compiler"))
                download.get_compiler()

            if choice_mod == 2:
                shutil.rmtree(os.path.join(os.getcwd(), ".pods/runtime"))
                download.get_runtime()

            return click.echo("Pulse pods has been successfully modified!")

        if choice == 3:
            return click.echo("Canceled!")

    download.get_compiler()
    download.get_runtime()
    return click.echo("Pulse pods has been successfully initialized!")
