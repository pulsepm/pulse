import os
import click
import tomli
import logging
import pulse.stroke.stroke as stroke

from typing import Union

from .pack_tar import tar_folder
from .pack_zip import zip_folder

def pack_folder(data: dict, version: str, platform: click.Choice(['windows', 'linux'], case_sensitive=False)) -> Union[str, bool]:

    # valid paths are only FOLDER/(component|plugins)
    expected_dirs: list[str] = ["plugins", "components"]
    unexpected_dirs: list[str] = [dir for dir in os.listdir(os.path.join(os.getcwd(), data[f"resources"][platform]["release_folder"]))
                                if os.path.isdir(os.path.join(os.getcwd(), data[f"resources"][platform]["release_folder"])) and dir not in expected_dirs]

    if not ('resources' in data and platform in data['resources']):
        logging.fatal("Fatal error occurred -> No resources table has been specified. Exit code: 42")
        stroke.dump(42)
        return False

    if not "release_folder" in data[f"resources"][platform]:
        logging.fatal("Fatal error occurred -> No release_folder has been specified within resources table. Exit code: 43")
        stroke.dump(43, f"[resource.{platform}] table.")
        return False

    elif not os.path.exists(data[f"resources"][platform]["release_folder"]):
        logging.fatal("Fatal error occurred -> release_folder has been specified within resources table, but it doesn't exists within current working directory. Exit code: 44")
        stroke.dump(44, f"[resource.{platform}] table.")
        return False
    
    if not os.listdir(os.path.join(os.getcwd(), data[f"resources"][platform]["release_folder"])):
        logging.fatal("Fatal error occurred -> release_folder has been specified within resources table and is present, but empty. Exit code: 45")
        stroke.dump(45, f"[resource.{platform}] table.")
        return False

    if unexpected_dirs:
        logging.fatal("Fatal error occurred -> Unexpected directory or file found within releases folder. Exit code: 48")
        stroke.dump(48, f"[resource.{platform}] table.")
        return False
    
    output_filename = f"{data['project']['repo']}-{version}-win32.zip" if platform == 'windows' else f"{data['project']['repo']}-{version}-linux.tar.gz"
    if platform == 'windows':
        zip_folder(data[f"resources"][platform]["release_folder"], output_filename)
    elif platform == 'linux':
        tar_folder(data[f"resources"][platform]["release_folder"], output_filename)

    return output_filename
