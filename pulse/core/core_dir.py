import os

HOME_DIR = os.path.expanduser("~")

# PPC
CONFIG_PATH = os.path.join(HOME_DIR, "Pulse Package Configuration", ".config")
RUNTIME_PATH = os.path.join(HOME_DIR, "Pulse Package Configuration", "runtime")
COMPILER_PATH = os.path.join(HOME_DIR, "Pulse Package Configuration", "compiler")
PACKAGE_PATH = os.path.join(HOME_DIR, "Pulse Package Configuration", "package")
PLUGINS_PATH = os.path.join(HOME_DIR, "Pulse Package Configuration", "plugins")

# CWD
REQUIREMENTS_PATH = os.path.join(os.getcwd(), "requirements")
PODS_PATH = os.path.join(os.getcwd(), ".pods")
