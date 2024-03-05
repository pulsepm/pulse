import click
import platform
import os
import pulse.core.git.git as git
from pulse.core.core_dir import COMPILER_PATH, RUNTIME_PATH


@click.command
@click.argument('type')
@click.argument('version')
def get(type: str, version: str) -> None:
    """
    Gets specified files used to debug or run open.mp server.

    User should input the desired type to download.
    It could be either a compiler or a runtime version.
    For now, only compiler for open.mp is 3.10.11,\
    which add support for 64-bit long names.

    Returns:
        None
    """
    return get_download(type, version)


def get_download(type: str, version: str) -> None:
    system = platform.system()
    if type == 'runtime':
        git.download_and_unzip_github_release(
            'openmultiplayer',
            'open.mp',
            version,
            'open.mp-win-x86.zip' if system == "Windows" else 'open.mp-linux-x86.tar.gz',
            RUNTIME_PATH
            )

        server_folder = os.path.join(RUNTIME_PATH, version)
        os.rename(os.path.join(RUNTIME_PATH, 'Server'), server_folder)

    elif type == 'compiler':
        git.download_and_unzip_github_release(
            'pulsepm',
            'compiler',
            version,
            f'pawnc-win-{version}.zip' if system == "Windows" else f'pawnc-linux-{version}.tar.gz',
            os.path.join(COMPILER_PATH, version)
            )

    else:
        click.echo('Invalid type.')
