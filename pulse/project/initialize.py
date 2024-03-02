import toml
import os
import sys
import pulse.core.git.git as git


def initialize(name: str, publisher: str, repo_name: str, entry: str = 'main.pwn') -> None:
    """
    Initialize a new Project instance.

    Args:
        name (str): The name of the project.
        type (int): The type of the project (1 for gamemode, 2 for library).
        publisher (str): The publisher or creator of the project.
        repo_name (str): The name of the repository.
    """

    project_table = {
        'name': name,
        'publisher': publisher,
        'repo': repo_name
    }

    data = {
        'project': project_table
    }

   # if any(os.listdir(current_dir)):
    #    print('Fatal error: Working directory must be empty.')
     #   return

    current_dir = os.getcwd()
    git.clone_github_repo('https://github.com/pulsepm/boilerplate', current_dir)
    toml_config = os.path.join(current_dir, 'pulse.toml')

    with open(toml_config, 'w') as toml_file:
        toml.dump(data, toml_file)
