import os
import toml
import click
import subprocess
from .choices import prompt_choices

toml_data = None

def exists() -> bool:
    """
    Check if the Pulse configuration file exists.

    Returns:
        bool: True if the configuration file exists, False otherwise.
    """
    home_dir = os.path.expanduser("~")
    config_path = os.path.join(home_dir, 'Pulse Package Configuration', '.config', 'pulseconfig.toml')
    print(config_path)

    return os.path.exists(config_path)

def write(data: dict, mode: str) -> None:
    """
    Write data to the Pulse configuration file.

    Args:
        data (dict): The data to be written to the configuration file.
        mode (str): The file open mode ('w' for write, 'a' for append, etc.).

    Raises:
        PermissionError: If there's a permission error during file writing.
    """
    home_dir = os.path.expanduser("~")
    config_path = os.path.join(home_dir, 'Pulse Package Configuration', '.config')
    file_name = 'pulseconfig.toml'
    full_path = os.path.join(config_path, file_name)

    try:
        os.makedirs(config_path, exist_ok=True)

        with open(full_path, mode) as toml_file:
            toml.dump(data, toml_file)

        subprocess.run(["attrib", "+H", config_path], check=True)

    except PermissionError as pe:
        print('Permission error: ' + pe)


def modify(choice: int = 0, load_data: bool = False) -> None:
    """
    Modify the Pulse configuration based on user input.

    Args:
        choice (int): The user's choice (default is 0).
        load_data (bool): Flag to load data from the configuration file (default is False).

    Choices:
        1: Modify GitHub username.
        2: Modify GitHub access token.
        3: Print current configuration.
        4: Exit.

    Recursively calls itself after each modification.
    """
    global toml_data
    choice = prompt_choices(True)

    if load_data:
        toml_data = load()

    print('Choice is ' + str(choice))

    if choice == 1:
        git_name = click.prompt('Input your new username')
        toml_data['user'] = git_name
        modify(choice)

    elif choice == 2:
        git_token = click.prompt('Input your new github access token')
        toml_data['token'] = git_token
        modify(choice)

    elif choice == 3:
        print(toml_data)
        write(toml_data, 'w')

    elif choice == 4:
        exit()
    
    else:
        click.echo('Bravo, great! You\'ve choosen invalid option')

def create() -> None:
    """
    Create a new Pulse configuration file with user input.

    Prompts the user for GitHub username and access token.
    Writes the user input to the configuration file.
    """
    click.echo('Configuration file doesn\'t exist. Let\'s create a new one.')
    git_name = click.prompt('Input the github username.', type=str)
    git_token = click.prompt('Input the github access token.', type=str)
    data = {
        'last_username': git_name,
        'user': git_name,
        'token': git_token
    }

    write(data, 'w')

def load() -> dict:
    """
    Load data from the Pulse configuration file.

    Returns:
        dict: Dictionary containing configuration data.

    Raises:
        toml.TomlDecodeError: If there's an error decoding TOML data from the file.
    """
    home_dir = os.path.expanduser("~")
    config_path = os.path.join(home_dir, 'Pulse Package Configuration', '.config')
    file_name = 'pulseconfig.toml'
    full_path = os.path.join(config_path, file_name)

    toml_data = None
    try:
        with open(full_path, 'r') as file:
            toml_data = toml.load(file)
            print(toml_data)

    except toml.TomlDecodeError as e:
        print(f"Error decoding TOML: {e}")

    return toml_data