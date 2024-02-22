from ._types import *
from typing import Optional
import toml
import os
import sys
import zipfile
import tarfile
import requests
import pulse.core.git.git as git

markdown_content = """
# ^package_name^
Welcome to the documentation for ^package_name^.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Features](#features)
5. [Versioning](#versioning)
6. [Contributing](#contributing)
7. [License](#license)

## Introduction

<!-- Write a small introduction info about your package, such as what it's designed for, reason why
  it has been made... -->

## Installation

in_part_1

## Features

<!-- Write essay about your features. Here is table of contents if you need it

### Table of Contents

1. [Feature1](#feature1)
2. [Feature2](#feature2)

#### Feature1

#### Feature2

-->

## Versioning
<!-- Pulse offers users only 2 possible ways of versioning. Calendar and Semantic versioning, calver and semver.
If your project uses semantic versioning, known as semver, use this. -->

<!-- This project follows Semantic Versioning (SemVer). For more information, see semver.org. -->
<!-- Else use this. -->
<!-- This project follows Calendar Versioning (CalVer). For more information, see calver.org. -->

## Contributing

<!-- Write on how developers can help you by contributing. By it, we mean on opening issues, helping you, improving your package.. -->

<!-- Following part should be omitted if you aren't using any licenses.-->

<!-- ## License

```
license text
```-->
"""

install_part_gamemode = """
`pulse gamemode ^publisher^/^package_name^`
"""

install_part_library = """
`pulse install ^publisher^/^package_name^`
"""

def initialize(name: str, type: int, publisher: str, repo_name: str, entry: str = 'main.pwn') -> None:
    """
    Initialize a new Project instance.

    Args:
        name (str): The name of the project.
        type (int): The type of the project (1 for gamemode, 2 for library).
        publisher (str): The publisher or creator of the project.
        repo_name (str): The name of the repository.

    Raises:
        ValueError: If an invalid project type is provided.
    """

    project_table = {
        'name': name,
        'type': 'gamemode' if type == TYPE_GAMEMODE else 'library',
        'publisher': publisher,
        'repo': repo_name
    }

    data = {
        'project': project_table
    }

    current_dir = os.getcwd()
    toml_config = os.path.join(current_dir, 'pulse.toml')
    md_file = os.path.join(current_dir, 'README.md')

    #if any(os.listdir(current_dir)):
     #   print('Fatal error: Working directory must be empty.')
      #  return

    with open(toml_config, 'w') as toml_file:
        toml.dump(data, toml_file)

    with open(md_file, 'w') as md:
        md.write(markdown_content.replace('^package_name^', f'{name}')
        .replace('^publisher^', f'{publisher}')
        .replace('in_part_1', install_part_gamemode if type == TYPE_GAMEMODE else install_part_library))

