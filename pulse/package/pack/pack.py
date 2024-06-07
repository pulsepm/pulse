import os
import click

from .pack_tar import tar_folder
from .pack_zip import zip_folder

def pack_folder(name: str, version: str, folder_path: str, platform: click.Choice(['windows', 'linux'], case_sensitive=False)) -> None:
    output_filename = f"{name}-{version}-win32.zip" if platform == 'windows' else f"{name}-{version}-linux.tar.gz"
    if platform == 'windows':
        zip_folder(folder_path, output_filename)
    elif platform == 'linux':
        tar_folder(folder_path, output_filename)