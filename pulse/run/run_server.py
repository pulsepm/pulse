import subprocess
import logging


def server(file_name: str) -> int:
    """
    Runs open.mp server with specified config file.

    Args:
        file_name (str): Configuration file name.
    """
    if ".pods" in file_name:
        logging.info("Running the open.mp server with pods...")
    else:
        logging.info("Running the open.mp server with pulse...")

    server_arguments = ["-c", "config.json"]
    server_command = [file_name] + server_arguments

    subprocess.run(server_command)
