import os

import tomli_w

import pulse.core.git.git_clone as git_clone
import pulse.download.download as download


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
    project_dir = os.path.join(current_dir, name)
    project_table = {"name": name, "publisher": publisher, "repo": repo_name, "entry": entry, "output": output}

    server = None
    compiler_data = None

    if os.path.isdir(project_dir):
        print(f"Fatal error: Folder {name} already exists")
        return

    git_clone.clone_github_repo("https://github.com/pulsepm/boilerplate", current_dir)

    compiler = download.get_compiler(pods)
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
