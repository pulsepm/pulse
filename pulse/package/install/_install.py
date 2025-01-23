import os
import tomli
import re
import logging
import shutil
import json

from ...core.core_dir import safe_open, PROJECT_TOML_FILE, PACKAGE_PATH, REQUIREMENTS_PATH, CONFIG_FILE
from ..parse._parse import PACKAGE_RE, package_parse
from ...git.git import default_branch, valid_token

from git import Repo, GitCommandError

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

    # check if it cached
    pkg = __package_cached(package)
    if pkg:
        dst = os.path.join(REQUIREMENTS_PATH, os.path.basename(os.path.dirname(pkg)))
        logging.info(f"{package} has been cached already. Moving it to our project...")
        shutil.copytree(pkg, dst, dirs_exist_ok=True)
        deps = __gather_dependencies(package)
        __install_deps(deps)

    # clone it
    else:
        inst = __package_install(package)
        print("INST")
        if inst:
            print("inst1")
            deps = __gather_dependencies(package)
            print(deps)
            __install_deps(deps)

            



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


def __package_in_requirements(package, requirements_list):
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
    print("Installing dependencies")
    for dep in deps:
        print("Installing dependency", dep)
        inst = __package_install(dep)
        if inst:
            print(f"Package {dep} has been installed")
        else:
            print(f"Couldn't install {dep}")

    for dep in deps:
        deps_list = __gather_dependencies(dep)
        if not deps_list:
            print(f"No dependencies found for {dep}")
            continue

        __install_deps(deps_list)


def __gather_dependencies(package):

    parsed_package = package_parse(package)
    if not parsed_package:
        logging.error(f"Invalid package format: {package}")
        return False

    author, repo, _, ver = parsed_package
    cached_path = os.path.join(PACKAGE_PATH, author, repo, ver if ver else "default")

    t = safe_open(os.path.join(cached_path, "pulse.toml"), 'rb')
    if t:
        l = tomli.load(t)
        try:
            reqs = l["requirements"]["live"]
        except:
            reqs = []

    elif not t:
        t = safe_open(os.path.join(cached_path, "pawn.json"), 'r')
        if t:
            l = json.load(t)
            try:
                reqs = l["dependencies"]
            except KeyError:
                reqs = []

        elif not t:
            reqs = []

    # Now load the reqs list
    print("Gathered")


    return reqs


def __package_install(package):
    parsed_package = package_parse(package)
    if not parsed_package:
        logging.error(f"Invalid package format: {package}")
        return False

    author, repo, separator, version = parsed_package
    save_path = os.path.join(PACKAGE_PATH, author, repo, version if version else "default")
    if os.path.exists(save_path) and os.listdir(save_path):
        print("Package is already installed, skip")
        shutil.copytree(save_path, os.path.join(REQUIREMENTS_PATH, repo), dirs_exist_ok=True)
        return False

    version = default_branch([author, repo]) if not version else version

    token_file = safe_open(CONFIG_FILE, 'rb')
    token_data = tomli.load(token_file)
    token = token_data["token"]

    if valid_token(token):
        print("VALID")
    else:
        print("INVALID")

    if separator == "#":
        git_repo = Repo.clone_from(
            f"https://{{{token}}}@github.com/{author}/{repo}.git", save_path, single_branch=True
        )
        print(f"https://{{{token}}}@github.com/{author}/{repo}.git")
        git_repo.head.reset(commit=version, index=True, working_tree=True)
        print(f"Installed {author}/{repo}#{version}")

    elif separator == ":":
        try:
            git_repo = Repo.clone_from(f"https://{{{token}}}@github.com/{author}/{repo}", save_path)
        except GitCommandError:
            print("Git error, no repo")
            return False

        git = git_repo.git
        git.checkout(version)
        print(f"Installed {author}/{repo}#{version}")

    elif separator == "@":
        git_repo = Repo.clone_from(
            f"https://{{{token}}}@github.com/{author}/{repo}.git",
            save_path,
            single_branch=True,
            branch=version,
        )
    
    else: 
        print(f"TAJING {version}")
        git_repo = Repo.clone_from(
            f"https://{{{token}}}@github.com/{author}/{repo}.git",
            save_path,
            single_branch=True,
            branch=version,
        )

    shutil.copytree(save_path, os.path.join(REQUIREMENTS_PATH, repo), dirs_exist_ok=True)

    return git_repo