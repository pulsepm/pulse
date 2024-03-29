import os
import platform
import subprocess
import shutil

import click
import toml
import json

import pulse.download.download as download
from pulse.core.core_dir import RUNTIME_PATH, PODS_PATH, REQUIREMENTS_PATH
from pulse.ensure.ensure import ensure as ensure_packages
from pulse.run.run_server import server


@click.command
@click.option('--ensure', '-e')
def run(ensure: bool) -> None:

    # read the version
    if not os.path.exists(os.path.join(os.getcwd(), "pulse.toml")):
        print("This is not a pulse package!")
        return

    # Ensure all plugins are there (just run ensure)
    # read the toml
    data = {}
    json_data = {}
    pods = os.path.exists(os.path.join(os.getcwd(), ".pods")) and os.path.isdir(os.path.join(os.getcwd(), ".pods"))
    with open("pulse.toml", 'r') as toml_config:
        data = toml.load(toml_config)

    with open(os.path.join(RUNTIME_PATH, data['runtime']['version'], "config.json"), 'r') as json_file:
        json_data = json.load(json_file)

    if ensure:
        ensure_packages()

    system = platform.system()
    file_name = os.path.join(
        os.path.join(PODS_PATH, "runtime") if pods else os.path.join(RUNTIME_PATH, data['runtime']['version']), "omp-server.exe" if system == "Windows" else "omp-server"
    )

    # if pods, just run the server from 
    if not os.path.exists(file_name) and not pods:
        # read the toml
        if 'version' in data['runtime']:
            click.echo("There's no downloaded runtimes. Downloading the specified one...")
            download.get_asset('runtime', data['runtime']['version'])
        
        else:
            click.echo("No specified version") # Fatal here
            return

    # move plugins and add them to config.json
    # plugins should be moved to ppc/runtime/version/plugins and added to the respective config.json through pulse.toml or in .pods if pods
    # now loop through plugins

    runtime_plugins = os.path.join(PODS_PATH, 'runtime', 'plugins') if pods else os.path.join(RUNTIME_PATH, data['runtime']['version'], "plugins")

    for file in os.listdir(os.path.join(REQUIREMENTS_PATH, "plugins")):
        full_file = os.path.join(REQUIREMENTS_PATH, "plugins", file)
        print(full_file)
        if os.path.isfile(full_file):
            print("Nije fajl a jeste")
            os.makedirs(runtime_plugins, exist_ok=True)

            shutil.copy(full_file, runtime_plugins)
            # add them to config.json
            json_data['pawn']['legacy_plugins'].append(file)
            print(f"Plugins: {json_data['pawn']['legacy_plugins']}")
            
    with open(os.path.join(RUNTIME_PATH, data['runtime']['version'], "config.json"), 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    old_dir = os.getcwd()
    os.chdir(os.path.join(RUNTIME_PATH, data['runtime']['version']))
    server(file_name)
    #os.chdir(old_dir)
