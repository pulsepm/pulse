import os
import platform
import subprocess
import shutil

import click
import tomli
import json
import logging

import pulse.stroke.stroke as stroke
import pulse.download.download as download
from pulse.core.core_dir import RUNTIME_PATH, PODS_PATH, REQUIREMENTS_PATH
from pulse.package.package_ensure import ensure_packages
from pulse.run.run_server import server


@click.command
@click.option('--ensure', '-e', is_flag=True, default=False)
def run(ensure: bool) -> None:
    """
    Start the project.
    """

    # read the version
    if not os.path.exists(os.path.join(os.getcwd(), "pulse.toml")):
        logging.fatal("Fatal error occurred -> Not a valid Pulse package. Exit code: 2")
        stroke.dump(2)
        return

    # Ensure all plugins are there (just run ensure)
    # read the toml
    logging.debug("Gathering information...")
    data = {}
    json_data = {}
    pods = os.path.exists(PODS_PATH) and os.path.isdir(PODS_PATH)

    runtime_plugins = os.path.join(PODS_PATH, 'runtime', 'plugins') if pods else os.path.join(RUNTIME_PATH, data['runtime']['version'], "plugins")
    runtime_loc = os.path.join(RUNTIME_PATH, data['runtime']['version']) if not pods else os.path.join(PODS_PATH, "runtime")

    logging.debug("Informations gathered, loading from files...")

    with open("pulse.toml", 'rb') as toml_config:
        data = tomli.load(toml_config)

    # This should be built on pulse.toml
    with open(os.path.join(runtime_loc, "config.json"), 'r') as json_file:
        json_data = json.load(json_file)

    logging.info("Files has been parsed succesfully!")

    if ensure:
        ensure_packages()

    logging.debug("Determinating OS...")
    system = platform.system()
    file_name = os.path.join(
        os.path.join(PODS_PATH, "runtime") if pods else os.path.join(RUNTIME_PATH, data['runtime']['version']), "omp-server.exe" if system == "Windows" else "omp-server"
    )

    logging.debug("OS determinated. Checking for runtime...")

    # if pods, just run the server from
    if not os.path.exists(file_name) and not pods:
        # read the toml
        if 'version' in data['runtime']:
            logging.warning("There's no downloaded runtimes. Downloading the specified one...")
            download.get_asset('runtime', data['runtime']['version'])

        else:
            logging.fatal("Fatal error occurred -> Error cloning repository. Exit code: 31")
            stroke.dump(31)
            return

    # move plugins and add them to config.json
    # plugins should be moved to ppc/runtime/version/plugins and added to the respective config.json through pulse.toml or in .pods if pods
    # now loop through plugins
    logging.debug("Moving plugins and adding the to config.json.")
    json_data['pawn']['legacy_plugins'].clear()

    if os.path.exists(os.path.join(REQUIREMENTS_PATH, "plugins")):
        for file in os.listdir(os.path.join(REQUIREMENTS_PATH, "plugins")):
            full_file = os.path.join(REQUIREMENTS_PATH, "plugins", file)
            if os.path.isfile(full_file):
                os.makedirs(runtime_plugins, exist_ok=True)

                shutil.copy(full_file, runtime_plugins)
                # add them to config.json
                json_data['pawn']['legacy_plugins'].append(file)
                logging.debug(f"Appendend file: {file}")
    
    logging.info("Plugins has been moved succesfully.")
    

    #move the mode
    logging.debug("Moving the gamemode and setting it to config.json...")
    shutil.copy(os.path.join(os.getcwd(), data['project']['output']), os.path.join(runtime_loc, "gamemodes"))

    with open(os.path.join(runtime_loc, "config.json"), 'w') as json_file:
        json_data['pawn']['main_scripts'].clear()
        json_data['pawn']['main_scripts'].append(os.path.basename(data['project']['output'][:-4]))
        json.dump(json_data, json_file, indent=4)

    os.chdir(runtime_loc)
    server(file_name)
