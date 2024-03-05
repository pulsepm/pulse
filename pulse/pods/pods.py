import click
import os
import pulse.core.git.git as git
from ..get.get import get_download
from pulse.core.core_dir import COMPILER_PATH, RUNTIME_PATH
import shutil
compilers_dict: dict[int, str] = {}
runtimes_dict: dict[int, str] = {}


@click.command
def pods() -> None:
    """
    Initialize project isolation.

    """
    if not os.path.exists(os.path.join(os.getcwd(), 'pulse.toml')):
        return print('This is not a pulse package!')

    if os.path.exists(os.path.join(os.getcwd(), ".pods")):
        click.echo('Pulse pods have already been initialized!')
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
                install_compiler()

            if choice_mod == 2:
                shutil.rmtree(os.path.join(os.getcwd(), ".pods/runtime"))
                install_runtime()

            return click.echo("Pulse pods has been successfully modified!")

        if choice == 3:
            return click.echo("Canceled!")

    install_compiler_and_runtime()
    return click.echo("Pulse pods has been successfully initialized!")


def install_compiler() -> None:
    click.echo("Select the version of the compiler you would like to install.")
    for i, release in enumerate(git.get_github_compiler_releases(), start=1):
        compilers_dict[i] = release['name']
        click.echo(f"{i}. {release['name']}")

    compiler_choice = click.prompt("Enter your choice", type=click.IntRange(1, i))
    compiler_path = os.path.join(COMPILER_PATH, compilers_dict[compiler_choice])
    if not os.path.exists(compiler_path):
        click.echo("Compiler is not found in the cache, it will be downloaded.")
        click.echo(f"Downloading compiler ({compilers_dict[compiler_choice]})..")
        get_download("compiler", compilers_dict[compiler_choice])

    pods_compiler = os.path.join(os.getcwd(), ".pods/compiler")
    shutil.copytree(os.path.join(COMPILER_PATH, compilers_dict[compiler_choice]), pods_compiler)

def install_runtime() -> None:
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
        get_download("runtime", runtimes_dict[runtime_choice])

    pods_runtime = os.path.join(os.getcwd(), ".pods/runtime")
    shutil.copytree(os.path.join(RUNTIME_PATH, runtimes_dict[runtime_choice]), pods_runtime)

def install_compiler_and_runtime() -> None:
    install_compiler()
    install_runtime()
