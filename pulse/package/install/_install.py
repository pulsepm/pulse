import os
import tomli
import tomli_w
import re
import logging
import shutil
import json
import time

from ...core.core_dir import safe_open, PROJECT_TOML_FILE, PACKAGE_PATH, REQUIREMENTS_PATH, CONFIG_FILE
from ..parse._parse import PACKAGE_RE, package_parse
from ...git.git import default_branch, valid_token

from concurrent.futures import ThreadPoolExecutor, as_completed

from git import Repo, GitCommandError

installed_deps = {}


def install_all_packages():
    with safe_open(PROJECT_TOML_FILE, 'rb+') as t:
        l = tomli.load(t)

    __install_deps(l["requirements"]["live"])
    



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

    with safe_open(PROJECT_TOML_FILE, 'rb+') as t:
        l = tomli.load(t)
    # check for repo any user/repo
    if "requirements" in l and __package_in_requirements_list(package, l["requirements"]["live"]):
        return

    # check if it cached
    pkg = __package_cached(package)
    if pkg:
        dst = os.path.join(REQUIREMENTS_PATH, os.path.basename(os.path.dirname(pkg)))
        logging.info(f"{package} has been cached already. Moving it to our project...")
        shutil.copytree(pkg, dst, dirs_exist_ok=True)
        deps = __gather_dependencies(package)
        l.get("requirements", {}).get("live", []).append(package)
        with safe_open(PROJECT_TOML_FILE, 'rb+') as t:
            tomli_w.dump(l, t)

        if not deps:
            logging.warning(f"No dependencies found for {package}. Skipping...")
            return
        __install_deps(deps)

    # clone it
    else:
        inst = __package_install(package)
        if inst:
            l.get("requirements", {}).get("live", []).append(package)
            with safe_open(PROJECT_TOML_FILE, 'rb+') as t:
                tomli_w.dump(l, t)

            deps = __gather_dependencies(package)
            if not deps:
                logging.warning(f"No dependencies found for {package}. Skipping...")
                return
            __install_deps(deps)

            
def __package_install(package):
    parsed_package = package_parse(package)
    if not parsed_package:
        logging.error(f"Invalid package format: {package}")
        return False

    author, repo, separator, version = parsed_package

    if repo in installed_deps:
        logging.warning(f"Package {author}/{repo} has already been installed as {installed_deps[repo]['author']}/{repo}")
        return False
        
    save_path = os.path.join(PACKAGE_PATH, author, repo, version if version else "default")
    if __package_cached(package):
        logging.info(f"{package} has been cached already. Moving it to our project...")
        installed_deps[f"{repo}"] = {
            "author": author,
            "version": version
        }
        if not __package_in_requirements_dir(package):
            shutil.copytree(save_path, os.path.join(REQUIREMENTS_PATH, repo), dirs_exist_ok=True) # throws insufficient perms for .git
        return False

    version = default_branch([author, repo]) if not version else version

    with safe_open(CONFIG_FILE, 'rb') as token_file:
        token_data = tomli.load(token_file)
        token = token_data["token"]

    if valid_token(token):
        pass
    else:
        pass

    if separator == "#":
        git_repo = Repo.clone_from(
            f"https://{{{token}}}@github.com/{author}/{repo}.git", save_path, single_branch=True
        )
        git_repo.head.reset(commit=version, index=True, working_tree=True)
        logging.info(f"Installed {author}/{repo}#{version}")

    elif separator == ":":
        try:
            git_repo = Repo.clone_from(f"https://{{{token}}}@github.com/{author}/{repo}", save_path)
        except GitCommandError:
            logging.error("Git error, no repo")
            return False

        git = git_repo.git
        git.checkout(version)
        logging.info(f"Installed {author}/{repo}:{version}")

    elif separator == "@":
        git_repo = Repo.clone_from(
            f"https://{{{token}}}@github.com/{author}/{repo}.git",
            save_path,
            single_branch=True,
            branch=version,
        )
        logging.info(f"Installed {author}/{repo}@{version}")
    
    else:
        git_repo = Repo.clone_from(
            f"https://{{{token}}}@github.com/{author}/{repo}.git",
            save_path,
            single_branch=True,
            branch=version,
        )
        logging.info(f"Installed {author}/{repo}@{version}")

    shutil.copytree(save_path, os.path.join(REQUIREMENTS_PATH, repo), dirs_exist_ok=True)

    installed_deps[f"{repo}"] = {
        "author": author,
        "version": version
    }
    logging.info(f"Package {package} has been installed.")

    return git_repo


def __package_cached(package):
    parsed_package = package_parse(package)
    if not parsed_package:
        logging.error(f"Invalid package format: {package}")
        return False

    author, repo, _, ver = parsed_package
    cached_path = os.path.join(PACKAGE_PATH, author, repo, ver if ver else "default")
    if os.path.isdir(cached_path) and os.listdir(cached_path): 
        # not empty! Since no point of having a cached empty package?
        # Should we check if repo is broken?
        return cached_path

    return False


def __package_in_requirements_dir(package):
    parsed_package = package_parse(package)
    if not parsed_package:
        logging.error(f"Invalid package format: {package}")
        return False

    _, repo, _, _ = parsed_package
    req = os.path.join(REQUIREMENTS_PATH, repo)
    if os.path.isdir(req) and os.listdir(req): 
        return req

    return False


def __package_in_requirements_list(package, requirements_list):
    """
    Check if a package or its repo is in the requirements list.
    Suggest ensuring if it exists, otherwise suggest installation.
    """
    # BETTER ERROR HANDLING
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


def __install_deps(deps):
    logging.debug("Installing dependencies...")

    def install_dependency(dep):
        logging.debug(f"Installing dependency {dep}")
        __package_install(dep)


    def process_dependency(dep):
        deps_list = __gather_dependencies(dep)
        if not deps_list:
            logging.warning(f"No dependencies found for {dep}. Skipping.1..")
            return []

        return deps_list

    with ThreadPoolExecutor() as executor:
        executor.map(install_dependency, deps)

    with ThreadPoolExecutor() as executor:
        results = executor.map(process_dependency, deps)

    for deps_list in results:
        if deps_list:
            __install_deps(deps_list)


def __gather_dependencies(package):

    parsed_package = package_parse(package)
    if not parsed_package:
        logging.error(f"Invalid package format: {package}")
        return False

    author, repo, _, ver = parsed_package
    cached_path = os.path.join(PACKAGE_PATH, author, repo, ver if ver else "default")

    with safe_open(os.path.join(cached_path, "pulse.toml"), 'rb') as t:
        if t:
            l = tomli.load(t)
            try:
                reqs = l["requirements"]["live"]
            except KeyError:
                reqs = []
        else:
            # If pulse.toml not found, check for pawn.json
            with safe_open(os.path.join(cached_path, "pawn.json"), 'r') as t:
                if t:
                    l = json.load(t)
                    try:
                        reqs = l["dependencies"]
                    except KeyError:
                        reqs = []
                else:
                    # If both files fail, set reqs as an empty list
                    reqs = []

    # Now load the reqs list
    if reqs:
        logging.debug("Requirements has been gathered.")


    return reqs









