import os
import subprocess
import sys

import click
import tomli
import tomli_w

import pulse.config.config_choices as config
from pulse.core.core_dir import CONFIG_PATH
from .config_load import load, toml_data

import logging
import pulse.logs.logs



def exists() -> bool:
    """
    Check if the Pulse configuration file exists.

    Returns:
        bool: True if the configuration file exists, False otherwise.
    """
    logging.debug("Checking if configuration file is present...")
    full_path = os.path.join(CONFIG_PATH, "pulseconfig.toml")

    ret = os.path.exists(full_path)
    ret_str = "exists" if ret else "doesn't exist"
    logging.debug(f"Configuration file {full_path} {ret_str}!")

    return ret


def write(data: dict, mode: str) -> None:
    """
    Write data to the Pulse configuration file.

    Args:
        data (dict): The data to be written to the configuration file.
        mode (str): The file open mode ('w' for write, 'a' for append, etc.).

    Raises:
        PermissionError: If there's a permission error during file writing.
    """
    logging.debug("Writting data to config file...")
    full_path = os.path.join(CONFIG_PATH, "pulseconfig.toml")

    try:
        logging.debug("Making directories...")
        os.makedirs(CONFIG_PATH, exist_ok=True)

        with open(full_path, mode) as toml_file:
            tomli_w.dump(data, toml_file, multiline_strings=True)
            logging.info("Data written.")
        

    except PermissionError as pe:
        print("Permission error: " + pe)


def modify(choice: int = 0, load_data: bool = False) -> None:
    """
    Modify the Pulse configuration based on user input.

    Args:
        choice (int): The user's choice (default is 0).
        load_data (bool): Flag to load data from the configuration file\
        (default is False).

    Choices:
        1: Modify GitHub username.
        2: Modify GitHub access token.
        3. Set print of debug messages.
        4. Set print of info messages.
        5. Set stroke dumps.
        7: Exit with saving.
        7: Exit.

    Recursively calls itself after each modification.

    Returns:
        None
    """
    global toml_data
    logging.debug("Prompting configuration options...")
    choice = config.prompt_choices(True)

    if load_data:
        toml_data = load()

    logging.info("You've selected option " + str(choice))

    if choice == 1:
        git_name = click.prompt("Input your new username")
        toml_data["user"] = git_name
        logging.info("GitHub username has been modified.")
        modify(choice)

    elif choice == 2:
        git_token = click.prompt("Input your new GitHub access token")
        toml_data["token"] = git_token
        logging.info("GitHub access token has been modified.")
        modify(choice)

    elif choice == 3:
        log_power = click.prompt("Input log messages power:")
        toml_data["log"] = log_power
        logging.info("Pulse logging power has been modified.")
        modify(choice)

    elif choice == 5:
        stroke = click.confirm("Dump strokes?")
        toml_data["stroke"] = stroke
        logging.info("Pulse stroke dump automatization has been modified.")
        modify(choice)

    elif choice == 6:
        logging.debug("Saving the data..")
        write(toml_data, "wb")

    elif choice == 7:
        logging.debug("Exiting without data saving...")
        sys.exit()

    else:
        logging.error("Bravo, great! You've choosen invalid option")


def create() -> None:
    """
    Create a new Pulse configuration file with user input.

    Prompts the user for GitHub username and access token.
    Writes the user input to the configuration file.

    Returns:
        None
    """
    logging.warning("Configuration file doesn't exist. Let's create a new one.")
    git_name = click.prompt("Your GitHub username", type=str)
    git_token = click.prompt("Your GitHub access token (https://github.com/settings/personal-access-tokens/new)", type=str)
    data = {"last_username": git_name, "user": git_name, "token": git_token}
    logging.debug("File data created.")

    write(data, "wb")


