import toml
import os
import pulse.core.git.git as git


def initialize(name: str, publisher: str, repo_name: str, entry: str = 'main.pwn') -> None:
    """
    Initialize a new Project instance.

    Args:
        name (str): The name of the project.
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
    #    return

    current_dir = os.getcwd()
    git.clone_github_repo('https://github.com/pulsepm/boilerplate', current_dir)
    toml_config = os.path.join(current_dir, 'pulse.toml')
    readme = os.path.join(current_dir, 'README.md')

    with open(toml_config, 'w') as toml_file:
        toml.dump(data, toml_file)

    with open(readme, 'r+') as md_file:
        md_data = md_file.read()
        md_data = md_data.replace('^package_name^', project_table['name']).replace('^publisher^', project_table['publisher'])
        md_file.seek(0)
        md_file.truncate(0)
        md_file.write(md_data)
