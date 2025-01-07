import os
import platform
import pulse.download.download as download
import subprocess
import json
import tomli
import logging
import pulse.stroke.stroke_dump as stroke


from pulse.core.core_dir import COMPILER_PATH, REQUIREMENTS_PATH


def compile(
    entry: str,
    output: str,
    version: str,
    options: list,
    modules: list,
    legacy: list,
    requirements: dict,
) -> None:
    """
    Compiles given entry file to output.

    Parameters:
        entry (str): The entry file for building.
        output (str): The file entry will be built to.
        version (str): Version of the compiler.
        options (list): Options to use with compiler.
        modules (list): The list of modules to append to compiler include paths.
        legacy (list): The list of legacy libraries to append to compiler include paths.
        requirements (dict): The requirements.

    Returns:
        None
    """
    # let's just assume this is our scheme, correct this
    version_path_exe: str = os.path.join(
        COMPILER_PATH,
        version,
        "pawncc.exe" if platform.system() == "Windows" else "pawncc",
    )
    version_path_lib: str = os.path.join(
        COMPILER_PATH,
        version,
        "pawnc.dll" if platform.system() == "Windows" else "libpawnc.so",
    )

    if not os.path.exists(entry):
        logging.fatal(
            "Fatal error occurred -> Project doesn't have an entry point. Exit code: 32"
        )
        stroke.dump(60)
        return

    # check if version exists and if not, redownload it,
    # but check if it's broken (e.g. not having one file, or both)
    if not os.path.exists(version_path_exe) or not os.path.exists(version_path_lib):
        logging.warning("Your compiler is broken. Redownloading assets...")
        download.get_asset("compiler", version)

    if not options:
        logging.warning(
            "Options haven't been specified, using predefined set of options..."
        )
        options: list = ["-;+", "-d3", "-Z+", f"-o{output}"]

    else:
        # just append output
        logging.info("Options have been specified, appending...")
        options.append(f"-o{output}")  # later work with dicks
        logging.debug(f"{output} has been appended.")
    # Read the modules list

    if legacy:
        # append legacy paths
        logging.info("Legacy libraries found, appending...")
        for item in legacy:
            options.append(f"-i{item}")
            logging.debug(f"{item} has been appended.")

    if modules:
        logging.info("Modules found, appending...")
        for item in modules:
            options.append(f"-i{item}")
            logging.debug(f"{item} has been appended.")

    # requirements scan and add dependencies

    if os.path.exists(REQUIREMENTS_PATH) and (reqs := os.listdir(REQUIREMENTS_PATH)):
        logging.info("Requirements found, appending...")
        for folder in reqs:
            req_path: str = os.path.join(REQUIREMENTS_PATH, folder)

            if os.path.isdir(req_path):
                files: list = os.listdir(req_path)
                for file in files:
                    if file == ("pawn.json" or "pulse.toml"):
                        file_path: str = os.path.join(req_path, file)
                        with open(file_path, "r") as c:
                            data: dict = (
                                json.load(c) if file == "pawn.json" else tomli.load(c)
                            )
                            if "include_path" in data:
                                options.append(f'-i{req_path}/{data["include_path"]}')
                                logging.debug(
                                    f"{req_path}/{data['include_path']} has been appended."
                                )
                            else:
                                options.append(f"-i{req_path}")
                                logging.debug(f"{req_path} has been appended.")

    if os.path.exists(res := os.path.join("requirements", ".resources")) and (
        listx := os.listdir(res)
    ):
        logging.info("Resources are present, appending...")
        for folder in listx:
            options.append(f"-i{os.path.join(res, folder)}")
            logging.debug(f"{os.path.join(res, folder)} has been appended.")

    # now everything is fine, let's fire building with the options
    # create a path
    directory, file = os.path.split(output)
    if not directory == "":
        logging.debug("Creating the directory for output.")
        os.makedirs(directory, exist_ok=True)

    logging.debug("Running the compiler...")
    pawncc: str = [version_path_exe] + options + [entry]
    env: dict = os.environ.copy()
    env["LD_LIBRARY_PATH"] = os.path.join(COMPILER_PATH, version)

    subprocess.run(pawncc, env=env)
