import os
import shutil

import click

import pulse.core.git.git_get as git_get
from pulse.core.core_dir import COMPILER_PATH

from .download_asset import get_asset

compilers_dict: dict[int, str] = {}


def get_compiler(isolate: bool = True) -> str:
    """
    Prompts user to install specified compiler

    Returns:
        None
    """
    click.echo("Select the version of the compiler you would like to install.")
    for i, release in enumerate(git_get.get_github_compiler_releases(), start=1):
        compilers_dict[i] = release["name"]
        click.echo(f"{i}. {release['name']}")

    compiler_choice = click.prompt("Enter your choice", type=click.IntRange(1, i))
    compiler_path = os.path.join(COMPILER_PATH, compilers_dict[compiler_choice])
    if not os.path.exists(compiler_path):
        click.echo("Compiler is not found in the cache, it will be downloaded.")
        click.echo(f"Downloading compiler ({compilers_dict[compiler_choice]})..")
        get_asset("compiler", compilers_dict[compiler_choice])

    if isolate:
        pods_compiler = os.path.join(os.getcwd(), ".pods/compiler")
        shutil.copytree(
            os.path.join(COMPILER_PATH, compilers_dict[compiler_choice]), pods_compiler
        )

    else:
        pass  # Handle those being added to pulse.toml

    return compilers_dict[compiler_choice]
