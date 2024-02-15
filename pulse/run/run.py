import click
import os
import subprocess
import platform
import pulse.core.git.git as git
from pulse.core.core_dir import HOME_DIR, CONFIG_PATH, RUNTIME_PATH

@click.command
def run() -> int:
    # Check if server is installed in cache already, if not, install in cache, if env, just copy from cache 
    # check for omp server
    system = platform.system()
    file_name = os.path.join(RUNTIME_PATH, 'omp-server.exe' if system == "Windows" else 'omp-server')

    if not os.path.exists(os.path.join(os.getcwd(), 'pulse.toml')):
        return print('This is not a pulse package!')

    if not os.path.exists(file_name):
        #download https://api.github.com/repos/openmultiplayer/open.mp/releases/tags/v1.1.0.2612

       # git.download_and_unzip_github_release('openmultiplayer', 'open.mp', 'v1.1.0.2612', 'open.mp-win-x86.zip' if system == "Windows" else 'open.mp-linux-x86.tar.gz', RUNTIME_PATH_V1)
        
       click.echo('There\'s no downloaded runtimes. Use pulse get runtime')
    else:
        try:
            subprocess.run(file_name, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")