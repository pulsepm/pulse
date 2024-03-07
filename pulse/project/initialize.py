import toml
import os
import pulse.core.git.git as git
import pulse.download.download as download


def initialize(name: str, publisher: str, repo_name: str, pods: bool, entry: str = 'main.pwn') -> None:
    """
    Initialize a new Project instance.

    Args:
        name (str): The name of the project.
        publisher (str): The publisher or creator of the project.
        repo_name (str): The name of the repository.
    """

    current_dir = os.getcwd()
    project_table = {
        'name': name,
        'publisher': publisher,
        'repo': repo_name
    }

    server = None
    compiler_data = None

    if any(os.listdir(current_dir)):
        print('Fatal error: Working directory must be empty.')
        return

    git.clone_github_repo('https://github.com/pulsepm/boilerplate', current_dir)

    compiler = download.get_compiler(pods)
    runtime = download.get_runtime(pods)

    if not pods: #not isolated then just add the corresponding versions to toml
        server = {
            'version': runtime # Later with more options
        }

        compiler_data = {
            'version': compiler
        }
    

    data = {
        'project': project_table,
        'runtime': server,
        'compiler': compiler_data
    }

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
