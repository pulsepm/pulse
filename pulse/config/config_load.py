import tomli
import os
import pulse.stroke.stroke as stroke

from .config import create
from pulse.core.core_dir import CONFIG_PATH

toml_data = {}

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

    print("DEBUG: Loading the configuration file...")
    try:
        with open(full_path, "rb") as file:
            toml_data = tomli.load(file)
            print("INFO: Configuration has been loaded.")

    except FileNotFoundError:
        create()

    except tomli.TOMLDecodeError as e:
        print(f"STROKE: Fatal error occurred. Exit code: 2")
        stroke.dump(2, e)
        

    return toml_data
