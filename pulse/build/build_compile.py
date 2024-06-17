import os
import platform
import pulse.download.download as download
import subprocess
import shutil
import re
import json

from pulse.core.core_dir import COMPILER_PATH

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

    if requirements:
        # list through toml requirements
        print(requirements)
        for key, items in requirements.items():
            print(f"items: {items}")

            for item in items:
                requirement = re.split(r'/|@|:|#', str(item))[1].split('/')[0]
                print(f"requirement: {requirement}")

            # append them by reading json if there's json field include_path otherwise just append root
                if not f"-irequirements/{requirement}" in options:
                    if os.path.exists(os.path.join("requirements", requirement, "pawn.json")):
                        with open(os.path.join("requirements", requirement, "pawn.json"), 'r') as config:
                            config_data = json.load(config)
                            if "include_path" in config_data:
                                options.append('-irequirements/'+f'{requirement}/'+f'{config_data["include_path"]}')
                            else:
                                options.append('-irequirements/'+f'{requirement}')

                    print(f"OPTIONS: {options}")


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
