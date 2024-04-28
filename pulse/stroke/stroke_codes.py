from collections import namedtuple
from pulse.core.core_dir import CONFIG_PATH

Errors = namedtuple("Error", [
    "problem",
    "fix",
    "hints",
])

stroke_errors = {
    2: Errors("This is most likely caused by corrupt configuration file.", "In order to fix it you can either delete the configuration file or modify it correctly if you're familiar with TOML.", [f"Go to {CONFIG_PATH}", "Either delete or modify the .pulseconfig file."]),
    3: Errors("Invalid use of git command. In this case, it's most likely related to invalid repository being cloned as the starting repository.", "Report this problem to Pulse development team.", ["Go to https://github.com/pulsepm/pulse", "Click on issues.", "Click on the 'new issue' button.", "Select the bug report option.", "Explain the problem with given pattern and submit the issue."]),
    4: Errors("Failure to get release information.", "Look for the exit code log has outputed and open the issue on github.", ["Look for the code log has outputed.", "Go to https://github.com/pulsepm/pulse", "Click on issues.", "Click on the 'new issue' button.", "Select the bug report option.", "Explain the problem with given pattern and submit the issue."]),
    5: Errors("Server or client error.", "Check that the command entered is correct. You may also have been rate limited.", ["Look for the code log has outputed.", "Go to https://github.com/pulsepm/pulse", "Click on issues.", "Click on the 'new issue' button.", "Select the bug report option.", "Explain the problem with given pattern and submit the issue."]),
    6: Errors("Server response code is in the range of 400 - 600.", "Check that the command entered is correct. You may also have been rate limited.", ["Look for the code log has outputed.", "Go to https://github.com/pulsepm/pulse", "Click on issues.", "Click on the 'new issue' button.", "Select the bug report option.", "Explain the problem with given pattern and submit the issue."]),
}