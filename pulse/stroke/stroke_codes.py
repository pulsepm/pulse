from collections import namedtuple
from pulse.core.core_dir import CONFIG_PATH

Errors = namedtuple("Error", [
    "problem",
    "fix", 
    "hints",
])

# prefixes legend
# nothing is for general errors
# 1[code] config module error codes
# 2 git module error codes
# 3 run module
# 4 pack module

stroke_errors = {
    2: Errors("Invalid Pulse package.", "Initialize the package.", "Run 'pulse init' command."),
    11: Errors("Corrupt configuration file.", "In order to fix it you can either delete the configuration file or modify it correctly if you're familiar with TOML.", [f"Go to {CONFIG_PATH}", "Either delete or modify the .pulseconfig file."]),
    21: Errors("Invalid use of git command. In this case, it's most likely related to invalid repository being cloned as the starting repository.", "Report this problem to Pulse development team.", ["Go to https://github.com/pulsepm/pulse", "Click on issues.", "Click on the 'new issue' button.", "Select the bug report option.", "Explain the problem with given pattern and submit the issue."]),
    22: Errors("Failure to get release information.", "Look for the exit code log has outputed and open the issue on github.", ["Look for the code log has outputed.", "Go to https://github.com/pulsepm/pulse", "Click on issues.", "Click on the 'new issue' button.", "Select the bug report option.", "Explain the problem with given pattern and submit the issue."]),
    31: Errors("Runtime table is not present.", "Create 'runtime' table in 'pulse.toml'.", ["Open 'pulse.toml'.", "Declare 'runtime' table somewhere by writting '[runtime]'."]),
    32: Errors("Runtime version is not specified.", "Specify the runtime version in 'pulse.toml'.", ["Open 'pulse.toml'.", "Find the [runtime] table if it's present, otherwise declare it.", "Add version key with the string value holding the desired version of runtime."]),
    41: Errors("Invalid versioning pattern followed.", "Follow the proper versioning pattern you've selected when you'd ran 'pulse package' command.", ["If you've selected semver pattern, follow it with pattern MAJOR.MINOR.PATCH versions, otherwise if calver pattern has been selected follow YEAR.MONTH.DAY version pattern."]),
    42: Errors("No resources table has been specified.", "Specify the '[resources.PLATFORM]' within 'pulse.toml' file.", ["Open 'pulse.toml'.", "Input '[resources.PLATFORM]' anywhere.", "Change the 'PLATFORM' part with desired platform to release for. (linux or windows)"]),
    43: Errors("No 'release_folder' has been specified within resources table.", "Specify the value for 'release_folder' key within a '[resource.PLATFORM]' table.", ["Open 'pulse.toml'.", "Find a '[resource.PLATFORM]' table.", "Specify the value using 'release_folder = \"value\"' pattern."]),
    44: Errors("'release_folder' has been specified within resources table, but it doesn't exists within current working directory.", "Simply create the folder for your respective value specified in 'pulse.toml'.", ["Open 'pulse.toml'", "Find the 'release_folder' value. It should be within '[resource.PLATFORM]' table.", "Read the value.", "Create the folder with the exact specified value for the key within current working directory."]),
    45: Errors("'release_folder' has been specified within resources table and is present, but empty.", "Simply put some contet for releasing into the 'release_folder' folder, or don't use 'package' and 'release' command at all! No steps for this one.", []),
    46: Errors("No packed releases for any OS.", "Occurs when there are no files in both of 'release_folder' folders. Put some content into at least one of them.", ["Locate your 'release_folder' folders.", "Open them and put some content for releasing into them."]),
    47: Errors("Release has been staged already.", "Either use 'release' command or delete the .rel file.", ["If you want to release the staged release use 'pulse release' command, otherwise delete .rel file."]),
    48: Errors("Unexpected directory or file found within releases folder.", "Check your respective release folders. Only folders allowed there, are 'plugins' and 'components'.", ["Check your release folders.", "Find the invalid folders or any files outside of those folders.", "Delete them."]),
    5: Errors("Server or client error.", "Check that the command entered is correct. You may also have been rate limited.", ["Look for the code log has outputed.", "Go to https://github.com/pulsepm/pulse", "Click on issues.", "Click on the 'new issue' button.", "Select the bug report option.", "Explain the problem with given pattern and submit the issue."]),
    6: Errors("Server response code is in the range of 400 - 600.", "Check that the command entered is correct. You may also have been rate limited.", ["Look for the code log has outputed.", "Go to https://github.com/pulsepm/pulse", "Click on issues.", "Click on the 'new issue' button.", "Select the bug report option.", "Explain the problem with given pattern and submit the issue."]),
}