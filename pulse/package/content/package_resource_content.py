import requests
from typing import Literal
import os
import tomli
import json
from platform import system


def get_package_resources(directory, package_type: Literal["pulse", "sampctl"]) -> tuple[str] | None:
    try:
        with open(os.path.join(directory, "pulse.toml" if package_type == "pulse" else "pawn.json"), mode="rb" if package_type == "pulse" else "r") as f:
            if package_type == "pulse":
                resource = tomli.load(f)
            else:
                resource = json.load(f)

        if package_type == "pulse":
            return (resource["project"]["publisher"], resource["project"]["repo"], resource["resource"][system().lower()]["name"])

        else:
            index: int = 0 if resource["resources"][0]["platform"] == system().lower() else 1
            return (resource["user"], resource["repo"], resource["resources"][index]["name"])

    except:
        return None


def get_resource_plugins(directory, package_type: Literal["pulse", "sampctl"]) -> list[str] | None:
    try:
        with open(os.path.join(directory, "pulse.toml" if package_type == "pulse" else "pawn.json"), mode="rb" if package_type == "pulse" else "r") as f:
            if package_type == "pulse":
                resource = tomli.load(f)
            else:
                resource = json.load(f)

        if package_type == "pulse":
            return resource["resource"][system().lower()]["plugins"]

        else:
            index: int = 0 if resource["resources"][0]["platform"] == system().lower() else 1
            return resource["resources"][index]["plugins"] if resource["resources"][index]["archive"] is True else resource["resources"][index]["name"]

    except:
        return None


def get_resource_includes(directory, package_type: Literal["pulse", "sampctl"]) -> list[str] | None:
    try:
        with open(os.path.join(directory, "pulse.toml" if package_type == "pulse" else "pawn.json"), mode="rb" if package_type == "pulse" else "r") as f:
            if package_type == "pulse":
                resource = tomli.load(f)
            else:
                resource = json.load(f)

        if package_type == "pulse":
            return resource["resource"][system().lower()]["includes"]

        else:
            index: int = 0 if resource["resources"][0]["platform"] == system().lower() else 1
            return resource["resources"][index]["includes"]

    except:
        return None



def get_resource_repo(directory, package_type: Literal["pulse", "sampctl"]) -> str | None:
    try:
        with open(os.path.join(directory, "pulse.toml" if package_type == "pulse" else "pawn.json"), mode="rb" if package_type == "pulse" else "r") as f:
            if package_type == "pulse":
                resource = tomli.load(f)
            else:
                resource = json.load(f)

        if package_type == "pulse":
            return resource["project"]["repo"]

        else:
            return resource["repo"]

    except:
        return None 
    

def get_resource_files(directory, package_type: Literal["pulse", "sampctl"]):
    try:
        with open(os.path.join(directory, "pulse.toml" if package_type == "pulse" else "pawn.json"), mode="rb" if package_type == "pulse" else "r") as f:
            if package_type == "pulse":
                resource = tomli.load(f)
            else:
                resource = json.load(f)

        if package_type == "pulse":
            return resource["resource"][system().lower()]["files"]

        else:
            index: int = 0 if resource["resources"][0]["platform"] == system().lower() else 1
            return resource["resources"][index]["files"]

    except:
        return None 


def get_resource_file(plugin: str) -> str:
    file = re.search(r'[^\\/]*$', plugin)
    return file.group(0) if file else plugin
