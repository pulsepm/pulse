import os
import platform
import subprocess
import shutil

import click
import tomli
import json
import logging

import pulse.stroke as stroke
import pulse.download.download as download
from pulse.core.core_dir import RUNTIME_PATH, PODS_PATH, REQUIREMENTS_PATH
from pulse.package.package_ensure import ensure_packages
from pulse.run.run_server import server

from .run_convert import config_convert

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
    plugins = []
    pods = os.path.exists(PODS_PATH) and os.path.isdir(PODS_PATH)

    with open("pulse.toml", 'rb') as toml_config:
        data = tomli.load(toml_config)

    if not "runtime" in data and pods is False:
        logging.fatal("Fatal error occurred -> Runtime table is not present. Exit code: 31")
        stroke.dump(31)
        return

    runtime_plugins = os.path.join(PODS_PATH, 'runtime', 'plugins') if pods else os.path.join(RUNTIME_PATH, data['runtime']['version'], "plugins")
   
    if not "version" in data["runtime"] and pods is False:
        logging.fatal("Fatal error occurred -> Runtime version is not specified. Exit code: 32")
        stroke.dump(32)
        return
    
    runtime_loc = os.path.join(RUNTIME_PATH, data['runtime']['version']) if not pods else os.path.join(PODS_PATH, "runtime")

    logging.info("Informations gathered.")

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
        logging.warning("There's no downloaded runtimes. Downloading the specified one...")
        download.get_asset('runtime', data['runtime']['version'])

    # move plugins and add them to config.json
    # plugins should be moved to ppc/runtime/version/plugins and added to the respective config.json through pulse.toml or in .pods if pods
    # now loop through plugins
    logging.debug("Converting pulse.toml to config.json...")

    if os.path.exists(os.path.join(REQUIREMENTS_PATH, "plugins")):
        for file in os.listdir(os.path.join(REQUIREMENTS_PATH, "plugins")):
            full_file = os.path.join(REQUIREMENTS_PATH, "plugins", file)
            if os.path.isfile(full_file):
                os.makedirs(runtime_plugins, exist_ok=True)

                shutil.copy(full_file, runtime_plugins)
                # add them to pulse.toml
                plugins.append(file)
                logging.debug(f"Appendend file: {file}")

        
        logging.info("Plugins has been moved succesfully.")
    
    config_convert(os.path.join(os.getcwd(), 'pulse.toml'), os.path.join(runtime_loc, "config.json"))

    #move the mode
    logging.debug("Moving the gamemode and setting it to config.json...")
    if not os.path.isfile(os.path.join(os.getcwd(), data['project']['output'])):
        print("No output file") #STROKE!
        return

    shutil.copy(os.path.join(os.getcwd(), data['project']['output']), os.path.join(runtime_loc, "gamemodes"))

    with open(os.path.join(runtime_loc, "config.json"), 'r+') as json_file:
        json_data = json.load(json_file)
        if 'main_scripts' in json_data['pawn']:
            json_data['pawn']['main_scripts'].clear() 
        else:
            json_data['pawn']['main_scripts'] = []

        if 'legacy_plugins' in json_data['pawn']:
            json_data['pawn']['legacy_plugins'].clear()
        else:
            json_data['pawn']['legacy_plugins'] = []

        json_data['pawn']['main_scripts'].append(os.path.basename(data['project']['output'][:-4]))
        json_data['pawn']['legacy_plugins'].extend(plugins)
        json_file.seek(0)
        json_file.truncate()
        json.dump(json_data, json_file, indent=4)

    os.chdir(runtime_loc)
    server(file_name)
