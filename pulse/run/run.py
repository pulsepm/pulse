import os
import platform
import shutil

import click
import tomli
import json
import logging

import pulse.stroke.stroke as stroke
import pulse.download.download as download
from ..core.core_dir import RUNTIME_PATH, PODS_PATH, REQUIREMENTS_PATH
from ..package.content import get_resource_files
from ..package.package_ensure import ensure_packages

from .run_server import server
from .run_convert import config_convert


@click.command
@click.option("--ensure", "-e", is_flag=True, default=False)
def run(ensure: bool) -> None:
    """
    Start the project.

    Args:
        ensure (bool): Whether to run ensure proccess before running the server.
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

    with open("pulse.toml", "rb") as toml_config:
        data = tomli.load(toml_config)

    if "runtime" not in data and pods is False:
        logging.fatal(
            "Fatal error occurred -> Runtime table is not present. Exit code: 31"
        )
        stroke.dump(31)
        return

    try:
        runtime_plugins = (
            os.path.join(PODS_PATH, "runtime", "plugins")
            if pods
            else os.path.join(RUNTIME_PATH, data["runtime"]["version"], "plugins")
        )
    except KeyError as ke:
        logging.fatal(
            "Fatal error occurred -> Runtime version is not specified. Exit code: 32"
        )
        stroke.dump(32, ke)
        return

    print(pods)

    runtime_loc = (
        os.path.join(RUNTIME_PATH, data["runtime"]["version"])
        if not pods
        else os.path.join(PODS_PATH, "runtime")
    )

    logging.info("Informations gathered.")

    if ensure:
        ensure_packages()

    logging.debug("Determinating OS...")
    system = platform.system()
    file_name = os.path.join(
        (
            os.path.join(PODS_PATH, "runtime")
            if pods
            else os.path.join(RUNTIME_PATH, data["runtime"]["version"])
        ),
        "omp-server.exe" if system == "Windows" else "omp-server",
    )

    logging.debug("OS determinated. Checking for runtime...")

    # if pods, just run the server from
    if not os.path.exists(file_name) and not pods:
        # read the toml
        logging.warning(
            "There's no downloaded runtimes. Downloading the specified one..."
        )
        download.get_asset("runtime", data["runtime"]["version"])

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

    if os.path.exists(REQUIREMENTS_PATH) and (reqs := os.listdir(REQUIREMENTS_PATH)):
        for folder in reqs:
            req_path = os.path.join(REQUIREMENTS_PATH, folder)
            res_path = os.path.join(REQUIREMENTS_PATH, ".resources")
            print(req_path)
            files = get_resource_files(req_path, "sampctl")
            # repo = get_resource_repo(req_path, "sampctl")
            if files:
                for file in files.values():
                    print(req_path, file)
                    resource = os.path.join(res_path, folder)
                    dirname = os.path.dirname(file)
                    print(dirname)
                    if dirname:
                        print("DIRNAME")
                        os.makedirs(
                            (
                                os.path.join(PODS_PATH, "runtime", dirname)
                                if pods
                                else os.path.join(
                                    RUNTIME_PATH, data["runtime"]["version"], dirname
                                )
                            ),
                            exist_ok=True,
                        )
                        shutil.copy(
                            os.path.join(resource, file),
                            (
                                os.path.join(PODS_PATH, "runtime", dirname)
                                if pods
                                else os.path.join(
                                    RUNTIME_PATH, data["runtime"]["version"], dirname
                                )
                            ),
                        )
                    else:
                        shutil.copy(
                            os.path.join(resource, file),
                            (
                                os.path.join(PODS_PATH, "runtime")
                                if pods
                                else os.path.join(
                                    RUNTIME_PATH, data["runtime"]["version"]
                                )
                            ),
                        )

    config_convert(
        os.path.join(os.getcwd(), "pulse.toml"),
        os.path.join(runtime_loc, "config.json"),
    )

    # move the mode
    logging.debug("Moving the gamemode and setting it to config.json...")
    if not os.path.isfile(os.path.join(os.getcwd(), data["project"]["output"])):
        print("No output file")  # STROKE!
        return

    shutil.copy(
        os.path.join(os.getcwd(), data["project"]["output"]),
        os.path.join(runtime_loc, "gamemodes"),
    )

    with open(os.path.join(runtime_loc, "config.json"), "r+") as json_file:
        json_data = json.load(json_file)
        if "main_scripts" in json_data["pawn"]:
            json_data["pawn"]["main_scripts"].clear()
        else:
            json_data["pawn"]["main_scripts"] = []

        if "legacy_plugins" in json_data["pawn"]:
            json_data["pawn"]["legacy_plugins"].clear()
        else:
            json_data["pawn"]["legacy_plugins"] = []

        json_data["pawn"]["main_scripts"].append(
            os.path.basename(data["project"]["output"][:-4])
        )
        json_data["pawn"]["legacy_plugins"].extend(plugins)
        json_file.seek(0)
        json_file.truncate()
        json.dump(json_data, json_file, indent=4)

    os.chdir(runtime_loc)
    server(file_name)
