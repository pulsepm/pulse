import click
import os
import toml
import subprocess

from .build_compile import compile

@click.command
def build():
    data = {}

    if not os.path.exists(os.path.join(os.getcwd(), 'pulse.toml')):
        print('This is not pulse package.')
        return
    # pulse toml exists, read it
    with(open('pulse.toml', 'r')) as toml_file:
        data = toml.load(toml_file)

    # i just realized i might not need to check for pods folder and generally pods having the compiler folder so just go with cached compiler for now
    print(data) # check the data
    project_data = data['project']

    compiler_data = data['compiler']
    print(compiler_data)


    # read the compiler data
    compile(project_data['entry'], project_data['output'], compiler_data['version'], None if not 'options' in project_data else compiler_data['options'])
