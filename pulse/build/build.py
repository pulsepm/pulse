import click
import os
import tomli
import subprocess

from .build_compile import compile

@click.command
@click.argument("mode", default="__global__mode__")
def build(mode: str):
    """
    Build the project.
    """
    data = {}

    if not os.path.exists(os.path.join(os.getcwd(), 'pulse.toml')):
        click.echo('This is not pulse package.')
        return
    # pulse toml exists, read it
    with(open('pulse.toml', 'rb')) as toml_file:
        data = tomli.load(toml_file)

    # i just realized i might not need to check for pods folder and generally pods having the compiler folder so just go with cached compiler for now
    project_data = data['project']
    requirements = data.get('requirements')
    print(requirements)

    if not 'compiler' in data:
        click.echo("You have to specify compiler options using [compiler] table.")
        return

    compiler_data = data['compiler']

    # read the compiler data
    if mode == "__global__mode__":
        if not 'version' in compiler_data:
            click.echo("You don't have compiler version specified in your pulse.toml. Please specify it via `version = (version)` key, within compiler table or your compiler profile table.")
            return

        compile(project_data['entry'], project_data['output'], compiler_data['version'], None if not 'options' in compiler_data else compiler_data['options'], None if not 'modules' in compiler_data else compiler_data['modules'], None if not 'legacy' in compiler_data else compiler_data['legacy'], None if not 'requirements' in data else requirements)

    else:
        if not 'profiles' in compiler_data:
            click.echo("You don't have profiles list.")
            return

        if not mode in compiler_data['profiles']:
            click.secho('Unexisting profile selected.', fg='red')
            return

        profile_data = compiler_data['profiles'][f'{mode}']

        if not 'version' in profile_data:
            click.echo("You don't have compiler version specified in your pulse.toml. Please specify it via `version = (version)` key, within compiler table or your compiler profile table.")
            return

        compile(project_data['entry'], project_data['output'], profile_data['version'], None if not 'options' in profile_data else profile_data['options'], None if not 'modules' in profile_data else profile_data['modules'], None if not 'legacy' in profile_data else profile_data['legacy'], None if not 'requirements' in data else requirements)