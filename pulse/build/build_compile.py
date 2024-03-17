import os
import platform
import pulse.download.download as download
import subprocess

from pulse.core.core_dir import COMPILER_PATH

def compile(entry, output, version, options: list):
    # check if entry exists

    # let's just assume this is our scheme, correct this
    version_path_exe = os.path.join(COMPILER_PATH, version, "pawncc.exe" if platform.system() == "Windows" else "pawncc")
    version_path_lib = os.path.join(COMPILER_PATH, version, "pawnc.dll" if platform.system() == "Windows" else "pawnc.so")

    if not os.path.exists(entry):
        return print("Project doesn't have an entry point.")

    # check if version exists and if not, redownload it, but check if it's broken (e.g. not having one file, or both)
    if not os.path.exists(version_path_exe) or not os.path.exists(version_path_lib):
        print("Your compiler is broken. Redownloading assets...")
        download.get_asset("compiler", version)

    if not options:
        print("no options")
        options = ["-;+", "-d3", "-Z+", f"-o{output}"]

    else:
        #just append output
        options.append(f"-o{output}") # later work with dicks

    # now everything is fine, let's fire building with the options
    pawncc = [version_path_exe] + options + [entry]
    subprocess.run(pawncc)



    