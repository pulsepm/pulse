# Pulse Package Manager (PPM) for open.mp

Pulse Package Manager (PPM) is a comprehensive package manager designed specifically for open.mp (Open Multiplayer), a multiplayer modification for Grand Theft Auto: San Andreas. PPM streamlines the management of dependencies, configurations, and project settings within open.mp projects, facilitating easier development and deployment processes.

## Features

- **Dependency Management**: Seamlessly manage project dependencies, including plugins, libraries, and runtime environments, ensuring compatibility and efficiency in development.
- **Configuration**: Configure project settings such as GitHub credentials, compiler profiles, and project metadata to tailor the development environment to your needs.
- **Project Isolation**: Isolate projects using Pods to maintain clean and consistent development environments, preventing conflicts and ensuring reproducibility.
- **Package Installation**: Install, update, and uninstall packages with support for branches, tags, and commits, simplifying the integration of third-party components into projects.
- **Automatic Dependency Resolution**: Automatically resolve and install dependencies for added packages, reducing manual effort and ensuring consistency across environments.
- **Project Initialization**: Initialize new open.mp projects with user-defined settings and configurations, streamlining the setup process for new development endeavors.

## Installation and Updating
### Linux
#### Install Script (Recommended)
Execute the script to install (or update if necessary) `pulse`.
```sh
curl -sSL https://raw.githubusercontent.com/pulsepm/pulse/main/install.sh | bash
```

### Manual Installation
1. Download the latest version of pulse from our [releases](https://github.com/pulsepm/pulse/releases).

2. Mark the downloaded binary as executable:
```sh
chmod u+x pulse
```

3. (Optional) Move it to a location that's defined in your `$PATH`:
```sh
mv pulse /usr/local/bin/ # sudo permissions are required by this specific path
```

### Development Installation
To set up a development environment, ensure you have `pip` installed (it may be packaged as `pip` or `pip3` on your system).

1. Clone the repository:
```sh
git clone https://github.com/pulsepm/pulse
```

2. Navigate to the project directory:
```sh
cd pulse
```

3. Create and activate a virtual environment:
```sh
virtualenv venv --distribute && source venv/bin/activate
```

4. Install the required dependencies:
```sh
pip install -r requirements.txt
```

5. (Optional) Create a script for easier launching pulse
Make sure `~/.local/bin` is in your `$PATH`.
```sh
echo "python3 $(pwd)/pulse.py \"\$@\"" > ~/.local/bin/pulse && chmod u+x ~/.local/bin/pulse
```

## Contributing

Contributions to Pulse Package Manager are welcome! If you encounter any issues or have suggestions for improvement, please feel free to open an issue or submit a pull request on the GitHub repository.

## Getting Started

1. Install Pulse Package Manager.
2. Initialize a new open.mp project using `pulse init`.
3. Configure project settings and dependencies using `pulse config` and `pulse install`.
4. Build and run your project using `pulse build` and `pulse run`.
5. Enjoy streamlined project management with Pulse Package Manager!

## Usage

To utilize Pulse Package Manager in your open.mp project, install Pulse and execute the desired commands in your project directory. Refer to the command syntax and examples provided above for detailed usage instructions.

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

## License

Pulse Package Manager is licensed under the [MIT License](LICENSE).
```

This enhanced Markdown document provides a comprehensive overview of Pulse Package Manager (PPM) tailored specifically for open.mp projects, with detailed explanations of commands, configurations, and usage guidelines.
