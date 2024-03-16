import os

HOME_DIR = os.path.expanduser("~")
CONFIG_PATH = os.path.join(HOME_DIR, "Pulse Package Configuration", ".config")
RUNTIME_PATH = os.path.join(HOME_DIR, "Pulse Package Configuration", "runtime")
COMPILER_PATH = os.path.join(HOME_DIR, "Pulse Package Configuration", "compiler")
PACKAGE_PATH = os.path.join(HOME_DIR, "Pulse Package Configuration", "package")
REQUIREMENTS_PATH = os.path.join(HOME_DIR, "Pulse Package Configuration", "requirements")