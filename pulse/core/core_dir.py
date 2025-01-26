import os
from platform import system

from contextlib import contextmanager

PROJECT_NAME = "pulsepm"

is_windows = system() == "Windows"

# Follow XDG specification on unix systems (if available) and use AppData for Windows 
if is_windows:
    CONFIG_PATH = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', PROJECT_NAME, 'config')
    data_dir = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', PROJECT_NAME, 'data')
    STROKE_PATH = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', PROJECT_NAME, 'stroke')
else:
    CONFIG_PATH = os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.expanduser("~/.config")), PROJECT_NAME)
    data_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser("~/.local/share")), PROJECT_NAME)
    STROKE_PATH = os.path.join(os.environ.get('XDG_STATE_HOME', os.path.expanduser("~/.local/state")), PROJECT_NAME)

CONFIG_FILE = os.path.join(CONFIG_PATH, "pulseconfig.toml")

# Define other directories within the project directory
RUNTIME_PATH = os.path.join(data_dir, "runtime")
COMPILER_PATH = os.path.join(data_dir, "compiler")
PACKAGE_PATH = os.path.join(data_dir, "package")
PLUGINS_PATH = os.path.join(data_dir, "plugins")

# CWD
REQUIREMENTS_PATH = os.path.join(os.getcwd(), "requirements")
PODS_PATH = os.path.join(os.getcwd(), ".pods")
PROJECT_TOML_FILE = os.path.join(os.getcwd(), "pulse.toml")
PROJECT_JSON_COMPAT_FILE = os.path.join(os.getcwd(), "pawn.json")

@contextmanager
def safe_open(p: str, mode: str):
    try:
        file = open(p, mode)
        yield file
    except FileNotFoundError:
        print(f"Error: The file '{p}' was not found.")
        yield None
    except PermissionError:
        print(f"Error: You do not have permission to open the file '{p}'.")
        yield None
    except IOError as e:
        print(f"Error: An IOError occurred while opening the file '{p}'.\nDetails: {e}")
        yield None
    finally:
        if 'file' in locals() and not file.closed:
            file.close() 

