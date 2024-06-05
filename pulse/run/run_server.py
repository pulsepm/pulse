import subprocess
import logging

def server(file_name: str) -> int:
    if '.pods' in file_name:
        logging.info(f"Running the open.mp server with pods...")
    else:
        logging.info(f"Running the open.mp server with pulse...")

    server_arguments = ['-c', 'config.json']
    server_command = [file_name] + server_arguments
    
    subprocess.run(server_command)