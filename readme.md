# Pulse Package Manager (PPM)

Pulse Package Manager (PPM) is a command-line tool designed to streamline the management of dependencies, configurations, and project settings within Pulse projects. By providing a set of intuitive commands, PPM simplifies tasks such as project initialization, dependency management, configuration, and project isolation.

## Features

- **Dependency Management**: Easily manage project dependencies, including plugins, libraries, and runtime environments.
- **Configuration**: Configure project settings such as GitHub credentials, compiler profiles, and project metadata.
- **Project Isolation**: Isolate projects using Pods, ensuring clean and consistent environments for development and execution.
- **Package Installation**: Install, update, and uninstall packages with support for branches, tags, and commits.
- **Automatic Dependency Resolution**: Automatically resolve and install dependencies for added packages.
- **Project Initialization**: Initialize new Pulse projects with user-defined settings and configurations.

## Commands

### `pulse config`

Configures Pulse by modifying GitHub credentials and other project settings. Offers options to modify existing configurations or create a new one.

### `pulse init`

Initializes a new Pulse project by prompting the user to provide project details such as GitHub username, project name, repository name, entry file name, and whether to initialize a GitHub repository or use Pods for project isolation.

### `pulse build [PROFILE]`

Builds the pawn file using specified compiler profiles from `pulse.toml`. If no profile is specified, it uses the global compiler profile. Adds legacy list, modules list, and dependencies from the `requirements` folder as include paths.

### `pulse run`

Runs the server, utilizing the version specified in `pulse.toml` or the version installed in the `.pods` folder. Automatically installs missing server versions and adds plugins from `requirements/plugins` folder.

### `pulse pods`

Initializes project isolation by creating a `.pods` folder and installing a compiler or runtime of a specified version.

### `pulse install [PACKAGE]`

Installs a Pulse package, including its dependencies, plugins, and configuration. Supports branch, tag, and commit specifications.

### `pulse uninstall [PACKAGE] [OPTIONS]`

Uninstalls a Pulse package and its dependencies. Supports recursive removal to remove all dependencies of the specified package.

### `pulse ensure`

Ensures that all packages specified in `pulse.toml` are present by copying them from the Pulse Package Configuration to the `requirements` folder, installing them if necessary.

## Usage

To utilize Pulse Package Manager in your project, simply install Pulse and execute the desired commands in your project directory. Refer to the command syntax and examples provided above for detailed usage instructions.

## Getting Started

1. Install Pulse Package Manager.
2. Initialize a new Pulse project using `pulse init`.
3. Configure project settings and dependencies using `pulse config` and `pulse install`.
4. Build and run your project using `pulse build` and `pulse run`.
5. Enjoy streamlined project management with Pulse Package Manager!

## Contributing

Contributions to Pulse Package Manager are welcome! If you encounter any issues or have suggestions for improvement, please feel free to open an issue or submit a pull request on the GitHub repository.

## License

Pulse Package Manager is licensed under the [MIT License](LICENSE).
