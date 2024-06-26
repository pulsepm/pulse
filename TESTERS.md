### toml file
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
live = [ "Ykpauneu/pmtest@main",]

[compiler]
version = "3.10.11"
options = [ "-d3", "-;+"]

[compiler.profiles.dev]
version = "3.10.11"
options = [ "-d3",]
```
    
I think this is pretty self explanatory, except for the compiler. So `[compiler]` is basically global compiler profile, it is     executed upon executing `pulse build` with no additional arguments. Below it is the way how you implement profiles. Profiles     are meant to be run with `pulse build [profile]`

### config
##### Syntax:
    `pulse config`

##### Summary
    Configures Pulse.

##### Behavior
Prompts the user to configure Pulse, by modifying GitHub credentials. If a configuration file exists, it offers options to modify the existing configuration. If no configuration file exists, it prompts the user to create a new one. 
Welcome message is displayed at the beginning.

### init
##### Syntax:
    pulse init

##### Summary
    Initializes a new Pulse project.

##### Behavior
Upon user executing the command, it should load his last used username for the project while prompting users several questions about new project as in this way. 
    1. GitHub username
    2. Name for the project.
    3. Name for the repo.
    4. Name for the entry file.
    5. Initialize the github repo?
    6. Whether to isolate the project with Pods.

If the initalization of github repo was answered positively it should create the repo with given credentials via pulse configure. You need token also.

If the pulse isolation was answered positively, it will run pulse pods for isolation. More below.

### build
##### Syntax:
    `pulse build [PROFILE]`

##### Summary
Builds the pawn file.

##### Argument
    `Profile: str`
Profile is an argument which is specified by string representation of a profile within pulse.toml

##### Behavior
Upon executing the command it runs the pawncc with options specified within pulse.toml file. 
If no options are present, it has default list of options. User can specify the build profiles specified in pulse.toml.
If specified profile is not present, it will show an error, aborting the compilation.

pawncc uses entry file and outputs the amx as output.
    
It also adds legacy list and modules list as include paths as well as `project_folder/requirements`

### run
##### Syntax
    `pulse run`

##### Summary
Runs the server

##### Behavior
Upon executing the command, it executes omp-server. If .pods folder is present it ignores the version within pulse.toml and executes the one within .pods folder, otherwise it uses version in pulse.toml as a representation for the server. If version specified is not present (installed) it will install them automatically. Note that upon executing, it adds plugins from `project_folder/requirements/plugins` into `plugins` folder of the server also it moves the output file so the server has to execute something.

### pods
##### Syntax:
    pulse pods

##### Summary:
Initialize project isolation.

##### Behavior:
Initializes project isolation by creating a `.pods` folder and installing a compiler or runtime of a certain version (taken from the cache or downloaded).

### install
##### Syntax:
    pulse install [PACKAGE]

##### Arguments:
    package: str
Package name. Branch, commit or tag specification is supported.
| syntax  | meaning
|----|-------
| @  | branch
| == | tag
| :  | commit

##### Summary:
Install a pulse package.

##### Example:
    pulse install Ykpauneu/pmtest@main

##### Behavior:
The package is installed by checking for the `pulse.toml` file, if it exists, the package will be loaded, then the dependencies will be loaded (including dependencies for dependencies). Also if the package contains a `*.dll` / `*.so` plugin it will be moved to the plugins folder. Similar actions will be performed in the `project_folder/requirements` folder. The package will also be written to pulse.toml.

### uninstall
##### Syntax:
    pulse uninstall [PACKAGE] [OPTIONS]

##### Arguments:
    package: str
Package name. Branch, commit or tag specification is supported (same for `pulse install`).

##### Options:
    --recursive
Removes the package with all dependencies.

##### Summary:
Uninstall pulse package.

##### Example:
    pulse uninstall Ykpauneu/pmtest==2.0.0

##### Behavior:
Removes the package from the Pulse Package Configuration and from `project_folder/requirements`. Note that the `--recursive` flag will also remove all dependencies of this package. After removal, the package entry will be deleted in `project_folder/pulse.toml`.

### ensure
##### Syntax:
    pulse ensure

##### Summary:
Ensures all packages are present.

##### Behavior:
Reads the packages specified in `project_folder/pulse.toml`, then copies them from Pulse Package Configuration to `project_folder/requirements` (including plugins, dependencies, etc.), if they are not found they will be installed and automatically copied.
