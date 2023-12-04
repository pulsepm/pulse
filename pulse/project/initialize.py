from ._types import *
from typing import Optional
import toml

class Project:
    def __init__(self, name: str, type: int, publisher: str, repo_name: str) -> None:
        """
        Initialize a new Project instance.

        Args:
            name (str): The name of the project.
            type (int): The type of the project (1 for gamemode, 2 for library).
            publisher (str): The publisher or creator of the project.
            repo_name (str): The name of the repository.

        Attributes:
            name (str): The name of the project.
            type (int): The type of the project (1 for gamemode, 2 for library).
            publisher (str): The publisher or creator of the project.
            repo_name (str): The name of the repository.
            project_table (dict): A dictionary containing project details for creating a toml file.
            data (dict): A dictionary containing project data to be written to the toml file.

        Raises:
            ValueError: If an invalid project type is provided.
        """
        self.name = name
        self.type = type
        self.publisher = publisher
        self.repo_name = repo_name

        self.project_table = {
            'name': self.name,
            'type': 'gamemode' if self.type == TYPE_GAMEMODE else 'library',
            'publisher': self.publisher,
            'repo': self.repo_name
        }
        
        self.data = {
            'project': self.project_table
        }

        with open('pulse.toml', 'w') as toml_file:
            toml.dump(self.data, toml_file)
