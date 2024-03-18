import os
import platform
import pulse.download.download as download
import subprocess
import shutil

from pulse.core.core_dir import COMPILER_PATH

def compile(entry, output, version, options: list, modules: list, legacy: list):
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
        options = ["-;+", "-d3", "-Z+", f"-o{output}"]

    else:
        #just append output
        options.append(f"-o{output}") # later work with dicks
    # Read the modules list

    if legacy:
        #append legacy paths
        for item in legacy:
            options.append(f"-i{item}")

    print("To here 3")
    if modules:
        for item in modules:
            options.append(f"-i{item}")

    print(f"Here goes options: {options}")
    # now everything is fine, let's fire building with the options
    #create a path 
    directory, file = os.path.split(output)
    os.makedirs(directory, exist_ok=True)

    pawncc = [version_path_exe] + options + [entry]
    subprocess.run(pawncc)



    