import os
import tomli
import re
import logging

from ...core.core_dir import safe_open, PROJECT_TOML_FILE
from ..parse._parse import PACKAGE_RE, package_parse

'''
- user executes `pulse install user/repo`
- pulse checks if we are in a pulse project; if not: inform the user and exit;
- Check if such package exists in the config file; if so: inform the user, suggest ensuring
- Check if it's already installed (if the path in the project exists, if it does remove it as we're about to reinstall it (from now on code for installing a new package and ensuring will be the same, so it should be good to abstract it))
- Check if we have it cached; if so: use it (copy it to our project or create a symlink)
- If it's not cached, check if the repository is valid on github (unless you also add custom git handlers which would be dope)
- In case of valid repository, cache it and either symlink or copy it to our local project as a git repo
- Update pulse.toml 
'''
def install_package(package):
    if not os.path.isfile(os.path.join(os.getcwd(), "pulse.toml")):
        return logging.fatal("STROKE!1, invalid project")

    t = safe_open(PROJECT_TOML_FILE, 'rb')
    l = tomli.load(t)
    # check for repo any user/repo
    if "requirements" in l and __package_in_requirements(package, l["requirements"]["live"]):
        return


def __package_in_requirements(package, requirements_list):
    """
    Check if a package or its repo is in the requirements list.
    Suggest ensuring if it exists, otherwise suggest installation.
    """
    if not requirements_list:
        logging.info("Requirements list is empty. Proceeding with installation.")
        return False

    parsed_package = package_parse(package) #check if valid also
    if not parsed_package:
        logging.error(f"Invalid package format: {package}")
        return False

    _, repo, _, _ = parsed_package

    duplicates = set()

    for requirement in requirements_list:
        parsed_requirement = package_parse(requirement)
        if parsed_requirement:
            _, req_repo, _, _ = parsed_requirement

            # Check if the repos match
            if repo == req_repo:
                duplicates.add(requirement)

    if duplicates:
        for duplicate in duplicates:
            logging.warning(
                    f"Multiple occurrences of {repo} -> {duplicate}. Skipping..."
                )
        return True

    # If we reach here, repo was not found
    logging.info(f"{repo} not found in the requirements. Proceeding with installation.")
    return False