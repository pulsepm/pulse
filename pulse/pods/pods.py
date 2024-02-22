import click
import platform
import os
import pulse.core.git.git as git
from ..get.get import get_download
from pulse.core.core_dir import COMPILER_PATH, RUNTIME_PATH
import shutil

@click.command
def pods() -> None:
    """
    Initialize project isolation

    """
    if not os.path.exists(os.path.join(os.getcwd(), 'pulse.toml')):
        return print('This is not a pulse package!')

    if os.path.exists(os.path.join(os.getcwd(), ".pods")):
        return print('Pulse pods have already been initialized!')

    compilers_dict = {}
    runtimes_dict = {}

    click.echo("Select the version of the compiler you would like to install.")
    for i, release in enumerate(git.get_github_compiler_releases(), start=1):
        compilers_dict[i] = release['name']
        click.echo(f"{i}. {release['name']}")

    compiler_choice = click.prompt("Enter your choice", type=click.IntRange(1, i))

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

    compiler_path = os.path.join(COMPILER_PATH, compilers_dict[compiler_choice])
    if not os.path.exists(compiler_path):
        click.echo("Compiler is not found in the cache, it will be downloaded.")
        click.echo(f"Downloading compiler ({compilers_dict[compiler_choice]})..")
        get_download("compiler", compilers_dict[compiler_choice])

    pods_runtime = os.path.join(os.getcwd(), ".pods/runtime")
    pods_compiler = os.path.join(os.getcwd(), ".pods/compiler")
    shutil.copytree(os.path.join(RUNTIME_PATH, runtimes_dict[runtime_choice]), pods_runtime)
    shutil.copytree(os.path.join(COMPILER_PATH, compilers_dict[compiler_choice]), pods_compiler)
    return click.echo("Pulse pods has been successfully initialized!")
