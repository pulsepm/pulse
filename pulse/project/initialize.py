import os

import tomli_w
import pulse.download.download as download

import platform
import subprocess

import git

import logging
import pulse.stroke.stroke as stroke

from pulse.core.core_url import Url

__BOILER_PLATE_URL: str = "https://github.com/pulsepm/boilerplate"


def initialize(
    name: str, publisher: str, repo_name: str, pods: bool, entry: str = "main.pwn", output: str = "main.amx"
) -> None:
    """
    Initialize a new Project instance.

    Args:
        name (str): The name of the project.
        publisher (str): The publisher or creator of the project.
        repo_name (str): The name of the repository.
    """

    current_dir = os.getcwd()
    project_dir = os.path.join(current_dir, repo_name)
    project_table = {"name": name, "publisher": publisher, "repo": repo_name, "entry": entry, "output": output}

    server = {}
    compiler_data = {}

    if os.path.isdir(project_dir):
        print(f"Fatal error: Folder {repo_name} already exists")
        return

    git_clone.clone_github_repo("https://github.com/pulsepm/boilerplate", project_dir)
    os.chdir(project_dir)

    compiler = download.get_compiler(False)
    runtime = download.get_runtime(pods)

    if not pods:  # not isolated then just add the corresponding versions to toml
        server = {"version": runtime}  # Later with more options

    
    compiler_data = {"version": compiler}

    data = {"project": project_table, "runtime": server, "compiler": compiler_data}

    toml_config = os.path.join(project_dir, "pulse.toml")
    readme = os.path.join(project_dir, "README.md")

    with open(toml_config, "wb") as toml_file:
        tomli_w.dump(data, toml_file, multiline_strings=True)

    with open(readme, "r+") as md_file:
        md_data = md_file.read()
        md_data = md_data.replace("^package_name^", project_table["name"]).replace(
            "^publisher^", project_table["publisher"]
        )
        md_file.seek(0)
        md_file.truncate(0)
        md_file.write(md_data)


def __initialize_boilerplate(destination_folder: str) -> None:
    """
    Initializes a project using boilerplate repository.

    Args:
        destination_folder (str): The local path where the repository will be cloned.

    Returns:
        None

    Raises:
        git.GitCommandError: If an error occurs during the cloning process.
    """
    try:
        logging.debug("Cloning boilerplate repo as a starting point...")
        git.Repo.clone_from(__BOILER_PLATE_URL, destination_folder)
        path = os.path.join(destination_folder, ".git")
        logging.debug("Determinating machine operative system...")
        if platform.system() == "Windows":
            subprocess.run(["cmd", "/c", "rd", "/s", "/q", path], check=True)
            logging.info("Windows operative system has been determinated.")
        else:
            subprocess.run(["rm", "-rf", path], check=True)
            logging.info("Linux operative system has been determinated.")

        logging.info(f"Repository cloned successfully to {destination_folder}")
    except git.GitCommandError as e:
        logging.fatal("Fatal error occurred -> Error cloning repository. Exit code: 21")
        stroke.dump(21, e)
        return
