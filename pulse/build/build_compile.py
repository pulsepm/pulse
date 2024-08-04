import os
import platform
import pulse.download.download as download
import subprocess
import shutil
import re
import json
import tomli

from pulse.core.core_dir import COMPILER_PATH, REQUIREMENTS_PATH

def compile(entry, output, version, options: list, modules: list, legacy: list, requirements: dict):

    # let's just assume this is our scheme, correct this
    version_path_exe = os.path.join(COMPILER_PATH, version, "pawncc.exe" if platform.system() == "Windows" else "pawncc")
    version_path_lib = os.path.join(COMPILER_PATH, version, "pawnc.dll" if platform.system() == "Windows" else "libpawnc.so")

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

    if modules:
        for item in modules:
            options.append(f"-i{item}")

    # requirements scan and add dependencies

    if os.path.exists(REQUIREMENTS_PATH) and (reqs := os.listdir(REQUIREMENTS_PATH)):
        for folder in reqs:
            print(folder)
            req_path = os.path.join(REQUIREMENTS_PATH, folder)

            if os.path.isdir(req_path):
                files = os.listdir(req_path)
                for file in files:
                    if file == ("pawn.json" or "pulse.toml"):
                        file_path = os.path.join(req_path, file)
                        print("AAAAA", file_path)
                        with open(file_path, 'r') as c:
                            data = json.load(c) if file == "pawn.json" else tomli.load(c)
                            if "include_path" in data:
                                options.append(f'-i{req_path}/{data["include_path"]}')
                            else:
                                options.append(f'-i{req_path}')

            

    
    if os.path.exists(res := os.path.join("requirements", ".resources")) and (listx := os.listdir(res)):
        print(listx)
        for folder in listx:
            options.append(f'-i{os.path.join(res, folder)}')

    print(f"Here goes options: {options}")
    # now everything is fine, let's fire building with the options
    # create a path
    directory, file = os.path.split(output)
    if not directory == "":
        os.makedirs(directory, exist_ok=True)

    pawncc = [version_path_exe] + options + [entry]
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = os.path.join(COMPILER_PATH, version)

    subprocess.run(pawncc, env=env)
