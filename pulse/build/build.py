import click
import os
import tomli
import logging
import pulse.stroke.stroke_dump as stroke

from .build_compile import compile
from ..core.core_dir import safe_open
from typing import IO


@click.command
@click.argument("mode", default="__global__mode__")
def build(mode: str) -> None:
    """
    Build the project.

    Parameters:
        mode (str): Compiler profile to fire the building proccess with.
    """
    data: dict = {}

    if not os.path.exists(os.path.join(os.getcwd(), "pulse.toml")):
        logging.fatal("Fatal error occurred -> Invalid pulse package. Exit code: 2")
        stroke.dump(2)
        return

    # pulse toml exists, read it
    toml_file: IO = safe_open("pulse.toml", "rb")
    data: dict = tomli.load(toml_file)

    # i just realized i might not need to check for pods folder and generally
    # pods having the compiler folder so just go with cached compiler for now

    project_data: dict = data["project"]
    requirements: dict = data.get("requirements")
    logging.info("Data parsed!")

    if "compiler" not in data:
        logging.fatal("Fatal error occurred -> Invalid compiler table. Exit code: 61")
        stroke.dump(61)
        return

    compiler_data: dict = data["compiler"]

    # read the compiler data
    if mode == "__global__mode__":
        if "version" not in compiler_data:
            logging.fatal(
                "Fatal error occurred -> Compiler version not specified. Exit code: 62"
            )
            stroke.dump(62, "'[compiler]' table.")
            return

        compile(
            project_data["entry"],
            project_data["output"],
            compiler_data["version"],
            None if "options" not in compiler_data else compiler_data["options"],
            None if "modules" not in compiler_data else compiler_data["modules"],
            None if "legacy" not in compiler_data else compiler_data["legacy"],
            None if "requirements" not in data else requirements,
        )

    else:
        if "profiles" not in compiler_data:
            logging.fatal("Fatal error occurred -> No compiler profiles. Exit code: 63")
            stroke.dump(63)
            return

        if mode not in compiler_data["profiles"]:
            logging.fatal(
                "Fatal error occurred -> Invalid profile selected. Exit code: 64"
            )
            stroke.dump(64)
            return

        profile_data = compiler_data["profiles"][f"{mode}"]

        if "version" not in profile_data:
            logging.fatal(
                "Fatal error occurred -> Compiler version not specified. Exit code: 62"
            )
            stroke.dump(62, f"'[compiler.profiles.{mode}]' table.")
            return

        compile(
            project_data["entry"],
            project_data["output"],
            profile_data["version"],
            None if "options" not in profile_data else profile_data["options"],
            None if "modules" not in profile_data else profile_data["modules"],
            None if "legacy" not in profile_data else profile_data["legacy"],
            None if "requirements" not in data else requirements,
        )
