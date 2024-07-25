# Pulse Package Manager (PPM) for open.mp

Pulse Package Manager (PPM) is a comprehensive package manager designed specifically for open.mp (Open Multiplayer), a multiplayer modification for Grand Theft Auto: San Andreas. PPM streamlines the management of dependencies, configurations, and project settings within open.mp projects, facilitating easier development and deployment processes.

## Documentation

Full documentation can be found here: https://pulse-package-manager.readthedocs.io/en/latest

## `pulse.toml` Configuration

```toml
[project]
name = "e"
publisher = "Mergevos"
repo = "e"
entry = "main.pwn"
output = "gm/main.amx"

[runtime]
version = "v1.2.0.2670"

[requirements]
live = [
    "Ykpauneu/pmtest@main",
]

[compiler]
version = "3.10.11"
options = [ "-d3", "-;+"]

[compiler.profiles.dev]
version = "3.10.11"
options = [ "-d3",]
```

## Commands

### `pulse config`

#### Syntax:
```
pulse config
```

#### Summary:
Configures Pulse.

#### Behavior:
The `pulse config` command prompts the user to configure Pulse by modifying various project settings, including GitHub credentials and other configuration parameters. If a configuration file already exists, it offers options to modify the existing configuration; otherwise, it guides the user through the process of creating a new configuration file. A welcome message is displayed at the beginning to guide the user through the configuration process.

### `pulse init`

#### Syntax:
```
pulse init
```

#### Summary:
Initializes a new Pulse project.

#### Behavior:
Upon executing the `pulse init` command, the user is prompted to provide details about the new open.mp project. These details include the user's GitHub username, project name, repository name, entry file name, and whether to initialize a GitHub repository or use Pods for project isolation. If the user chooses to initialize a GitHub repository, the tool creates the repository with the provided credentials via `pulse configure`. If project isolation with Pods is selected, the command runs `pulse pods` to set up project isolation.

### `pulse build [PROFILE]`

#### Syntax:
```
pulse build [PROFILE]
```

#### Summary:
Builds the pawn file.

#### Argument:
- `Profile: str`: Profile specified by a string representation within `pulse.toml`.

#### Behavior:
The `pulse build` command compiles the pawn file using options specified within the `pulse.toml` configuration file. If no options are present, it uses a default list of options. Users can specify build profiles defined in `pulse.toml`. If the specified profile is not present, an error is shown, aborting the compilation process. The command adds legacy list, modules list, and dependencies from the `requirements` folder as include paths.

### `pulse run`

#### Syntax:
```
pulse run
```

#### Summary:
Runs the open.mp server.

#### Behavior:
Executing the `pulse run` command launches the omp-server. If the `.pods` folder is present, the command ignores the version specified in `pulse.toml` and executes the version located within the `.pods` folder. Otherwise, it uses the version specified in `pulse.toml`. If the specified version is not installed, it is automatically installed. Additionally, the command adds plugins from `project_folder/requirements/plugins` into the `plugins` folder of the server and moves the output file so the server has an executable file.

### `pulse pods`

#### Syntax:
```
pulse pods
```

#### Summary:
Initialize project isolation.

#### Behavior:
The `pulse pods` command initializes project isolation by creating a `.pods` folder and installing a compiler or runtime of a specific version, which is taken from the cache or downloaded as needed.

### `pulse install [PACKAGE]`

#### Syntax:
```
pulse install [PACKAGE]
```

#### Arguments:
- `package: str`: Package name. Branch, commit, or tag specification is supported.

#### Summary:
Install a package for open.mp.

#### Example:
```
pulse install Ykpauneu/pmtest@main
```

#### Behavior:
The `pulse install` command installs the specified package, including its dependencies, plugins, and configuration. It supports branch, commit, or tag specifications. The tool checks for the existence of a `pulse.toml` file; if it exists, the package is loaded, and its dependencies are loaded recursively (including dependencies for dependencies). If the package contains a `*.dll` or `*.so` plugin, it is moved to the plugins folder. Similar actions are performed in the `project_folder/requirements` folder. The package is also added to `pulse.toml`.

### `pulse uninstall [PACKAGE] [OPTIONS]`

#### Syntax:
```
pulse uninstall [PACKAGE] [OPTIONS]
```

#### Arguments:
- `package: str`: Package name. Branch, commit, or tag specification is supported (same for `pulse install`).

#### Options:
- `--recursive`: Removes the package with all dependencies.

#### Summary:
Uninstall a package from open.mp.

#### Example:
```
pulse uninstall Ykpauneu/pmtest==2.0.0
```

#### Behavior:
The `pulse uninstall` command removes the specified package from the Pulse Package Configuration and from `project_folder/requirements`. If the `--recursive` flag is used, it removes all dependencies of the specified package as well. After removal, the package entry is deleted from `project_folder/pulse.toml`.

### `pulse ensure`

#### Syntax:
```
pulse ensure
```

#### Summary:
Ensures all packages are present.

#### Behavior:
The `pulse ensure` command reads the packages specified in `project_folder/pulse.toml`, then copies them from the Pulse Package Configuration to `project_folder/requirements` (including plugins, dependencies, etc.). If any packages are not found, they are installed and automatically copied.

## Uninstalling Pulse
### Linux
To uninstall Pulse and remove only the program binary, execute the following command in your terminal:
```sh
wget -qO- https://raw.githubusercontent.com/pulsepm/pulse/master/install.sh | bash -s -- --remove
```

To completely remove Pulse, including all associated configuration and cache directories, use the --remove-all option:
```sh
wget -qO- https://raw.githubusercontent.com/pulsepm/pulse/master/install.sh | bash -s -- --remove-all
```
The --remove-all option will delete all files and directories related to Pulse. Ensure you have backed up any important data before proceeding with this command.

## License

Pulse Package Manager is licensed under the [MIT License](LICENSE).
```

This enhanced Markdown document provides a comprehensive overview of Pulse Package Manager (PPM) tailored specifically for open.mp projects, with detailed explanations of commands, configurations, and usage guidelines.
