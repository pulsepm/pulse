import os
from platform import system

PROJECT_NAME = "pulsepm"

is_windows = system() == "Windows"

# Follow XDG specification on unix systems (if available) and use AppData for Windows 
if is_windows:
    CONFIG_PATH = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', PROJECT_NAME, 'config')
    data_dir = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', PROJECT_NAME, 'data')
else:
    CONFIG_PATH = os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.expanduser("~/.config")), PROJECT_NAME)
    data_dir = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser("~/.local/share")), PROJECT_NAME)

# Define other directories within the project directory
RUNTIME_PATH = os.path.join(data_dir, "runtime")
COMPILER_PATH = os.path.join(data_dir, "compiler")
PACKAGE_PATH = os.path.join(data_dir, "package")
PLUGINS_PATH = os.path.join(data_dir, "plugins")

# CWD
REQUIREMENTS_PATH = os.path.join(os.getcwd(), "requirements")
PODS_PATH = os.path.join(os.getcwd(), ".pods")
