import click
import os
import subprocess
import platform
import pulse.core.git.git as git

@click.command
def run() -> int:
    # Check if it's initialized as virtual env
    # check for omp server
    path = os.getcwd()
    system = platform.system()
    file_name = os.path.join(path, 'omp-server.exe' if system == "Windows" else 'omp-server')

    omp = os.path.join(path, file_name)
    if not os.path.exists(omp):
        #download https://api.github.com/repos/openmultiplayer/open.mp/releases/tags/v1.1.0.2612

        git.download_and_unzip_github_release('openmultiplayer', 'open.mp', 'v1.1.0.2612', 'open.mp-win-x86.zip' if system == "Windows" else 'open.mp-linux-x86.tar.gz')
        
        try:
            subprocess.run(file_name, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
    else:
        try:
            subprocess.run(file_name, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")