import os
import subprocess
import sys

import click
import tomli
import tomli_w

import pulse.config.config_choices as config
from pulse.core.core_dir import CONFIG_PATH

toml_data = None


def exists() -> bool:
    """
    Check if the Pulse configuration file exists.

    Returns:
        bool: True if the configuration file exists, False otherwise.
    """
    full_path = os.path.join(CONFIG_PATH, "pulseconfig.toml")
    print(CONFIG_PATH)

    return os.path.exists(full_path)


def write(data: dict, mode: str) -> None:
    """
    Write data to the Pulse configuration file.

    Args:
        data (dict): The data to be written to the configuration file.
        mode (str): The file open mode ('w' for write, 'a' for append, etc.).

    Raises:
        PermissionError: If there's a permission error during file writing.
    """
    full_path = os.path.join(CONFIG_PATH, "pulseconfig.toml")

    try:
        os.makedirs(CONFIG_PATH, exist_ok=True)

        with open(full_path, mode) as toml_file:
            tomli_w.dump(data, toml_file, multiline_strings=True)

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
        3: Print current configuration.
        4: Exit.

    Recursively calls itself after each modification.

    Returns:
        None
    """
    global toml_data
    choice = config.prompt_choices(True)

    if load_data:
        toml_data = load()

    print("Choice is " + str(choice))

    if choice == 1:
        git_name = click.prompt("Input your new username")
        toml_data["user"] = git_name
        modify(choice)

    elif choice == 2:
        git_token = click.prompt("Input your new github access token")
        toml_data["token"] = git_token
        modify(choice)

    elif choice == 3:
        print(toml_data)
        write(toml_data, "w")

    elif choice == 4:
        sys.exit()

    else:
        click.echo("Bravo, great! You've choosen invalid option")


def create() -> None:
    """
    Create a new Pulse configuration file with user input.

    Prompts the user for GitHub username and access token.
    Writes the user input to the configuration file.

    Returns:
        None
    """
    click.echo("Configuration file doesn't exist. Let's create a new one.")
    git_name = click.prompt("Input the github username.", type=str)
    git_token = click.prompt("Input the github access token.", type=str)
    data = {"last_username": git_name, "user": git_name, "token": git_token}

    write(data, "w")


def load() -> dict:
    """
    Load data from the Pulse configuration file.

    Returns:
        dict: Dictionary containing configuration data.

    Raises:
        tomli.TOMLDecodeError: If there's an error decoding TOML\
        data from the file.
    """
    global toml_data
    full_path = os.path.join(CONFIG_PATH, "pulseconfig.toml")

    try:
        with open(full_path, "rb") as file:
            toml_data = tomli.load(file)
            print(toml_data)

    except tomli.TOMLDecodeError as e:
        print(f"Error decoding TOML: {e}")

    return toml_data
