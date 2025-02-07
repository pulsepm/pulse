import os
import tomli
import json
import tomli_w
import logging
import shutil
import stat
from pathlib import Path
from git import Repo, GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from ...core.core_dir import safe_open, PROJECT_TOML_FILE, PACKAGE_PATH, REQUIREMENTS_PATH, CONFIG_FILE
from ..parse._parse import package_parse
from ...git.git import default_branch, valid_token

from concurrent.futures import ThreadPoolExecutor

from git import Repo, GitCommandError, InvalidGitRepositoryError, NoSuchPathError


class PackageInstaller:
    def __init__(self):
        self.installed_deps = {}
        self.package_path = Path(PACKAGE_PATH)
        self.requirements_path = Path(REQUIREMENTS_PATH)

    def install_all_packages(self):
        """Install all packages listed in project configuration."""
        with safe_open(PROJECT_TOML_FILE, 'rb') as t:
            config = tomli.load(t)
        self._install_deps(config["requirements"]["live"]) 

    def install_package(self, package: str) -> bool:
        """Install a single package and its dependencies."""
        if not os.path.isfile(PROJECT_TOML_FILE):
            logging.fatal("Invalid project: No pulse.toml found")
            return False

        with safe_open(PROJECT_TOML_FILE, 'rb') as t:
            config = tomli.load(t)

        if "requirements" in config and self._package_in_requirements_list(package, config["requirements"]["live"]):
            return False

        if self._install_single_package(package):
            self._append_dependency(package)
            
            deps = self._gather_dependencies(package)
            if deps:
                self._install_deps(deps)
            return True
        
        return False

    def _check_repository(self, path: Path) -> Repo | None:
        """Verify if repository exists and is valid."""
        try:
            repo = Repo(str(path))
            try:
                _ = repo.head.commit
                logging.info(f"Repository exists at {path}")
                return repo
            except Exception as e:
                logging.warning(f"Repository exists but is corrupted: {e}")
                if path.exists():
                    shutil.rmtree(str(path), onerror=self._handle_copy_error)
                return None

        except (InvalidGitRepositoryError, NoSuchPathError):
            logging.error(f"Repository doesn't exist at {path}")
            return None
        
        except Exception as e:
            logging.error(f"Unexpected error checking repository: {e}")
            return None

    def _install_single_package(self, package: str) -> bool:
        """Install a single package without dependencies."""
        parsed_package = package_parse(package)
        if not parsed_package:
            logging.error(f"Invalid package format: {package}")
            return False

        author, repo, separator, version = parsed_package

        if repo in self.installed_deps:
            logging.warning(f"Package {author}/{repo} already installed as {self.installed_deps[repo]['author']}/{repo}")
            return False

        save_path = self.package_path / author / repo / (version if version else "default")
    
        if self._package_cached(save_path):
            logging.info(f"{package} has been cached already. Moving it to project...")
            try:
                dst = self.requirements_path / repo
                 
                # Handle .git directory
                
                git_dir = dst / '.git'
                if git_dir.exists():
                    shutil.rmtree(git_dir, onerror=self._handle_copy_error)

                shutil.copytree(save_path, dst, dirs_exist_ok=True)
               
                
                self.installed_deps[repo] = {
                    "author": author,
                    "version": version if version else "default"
                }
                
                logging.info(f"Successfully moved cached package {package}")
                return True
                
            except Exception as e:
                logging.error(f"Failed to copy cached package: {e}")
                return False

        return self._clone_fresh_repository(author, repo, separator, version, save_path)

    def _handle_copy_error(self, function: Callable, path, info):
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)

    def _package_cached(self, path: Path) -> bool:
        """Check if package exists in cache and is valid."""
        try:
            if not path.is_dir():
                return False
                
            repo = self._check_repository(path)
            if repo is None:
                return False
                
            # Additional checks could be added here
            # For example, verify required files exis
            return True
            
        except Exception as e:
            logging.error(f"Error checking cache: {e}")
            return False

    def _clone_fresh_repository(self, author: str, repo: str, separator: str, version: str, save_path: Path) -> bool:
        """Clone a fresh copy of the repository."""
        try:
            with safe_open(CONFIG_FILE, 'rb') as token_file:
                token = tomli.load(token_file)["token"]
            
            if not valid_token(token):
                logging.error("Invalid GitHub token")
                return False

            version = version if version else default_branch([author, repo])
            repo_url = f"https://{{{token}}}@github.com/{author}/{repo}.git"

            if separator == "#":
                git_repo = Repo.clone_from(repo_url, str(save_path), single_branch=True)
                git_repo.head.reset(commit=version, index=True, working_tree=True)
            elif separator == ":":
                git_repo = Repo.clone_from(repo_url, str(save_path))
                git_repo.git.checkout(version)
            else: 
                git_repo = Repo.clone_from(repo_url, str(save_path), single_branch=True, branch=version)

            shutil.copytree(save_path, self.requirements_path / repo, dirs_exist_ok=True)

            self.installed_deps[repo] = {
                "author": author,
                "version": version if version else "default"
            }
            
            logging.info(f"Installed {author}/{repo}{separator}{version}")
            return True

        except GitCommandError as e:
            logging.error(f"Git error: {e}")
            if save_path.exists():
                shutil.rmtree(str(save_path), onerror=self._handle_copy_error)
            return False
        
        except Exception as e:
            logging.error(f"Unexpected error during clone: {e}")
            if save_path.exists():
                shutil.rmtree(str(save_path), onerror=self._handle_copy_error)
            return False

    def _update_repo_state(self, repo: Repo, version: str, force: bool) -> bool:
        """Update repository to specified version."""
        try:
            if force:
                repo.remote().pull()

            if version:
                if '#' in version:
                    repo.head.reset(commit=version, index=True, working_tree=True)
                else:
                    repo.git.checkout(version)
            else:
                repo.remote().pull()

            return True

        except Exception as e:
            logging.error(f"Error updating repository state: {e}")
            return False

    def _install_deps(self, deps):
        """Install multiple dependencies concurrently."""

        def install_dependency(dep):
            return self._install_single_package(dep)

        def process_dependency(dep):
            return self._gather_dependencies(dep)

        with ThreadPoolExecutor() as executor:
            executor.map(install_dependency, deps)

        with ThreadPoolExecutor() as executor:
            results = executor.map(process_dependency, deps)

        for deps_list in results:
            if deps_list:
                self._install_deps(deps_list)

    def _gather_dependencies(self, package):
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
                with safe_open(os.path.join(cached_path, "pawn.json"), 'r') as t:
                    if t:
                        l = json.load(t)
                        try:
                            reqs = l["dependencies"]
                        except KeyError:
                            reqs = []
                    else:
                        reqs = []

        return reqs

    def _append_dependency(self, package):
        """Appends the dependency to the project config file."""
        with safe_open(PROJECT_TOML_FILE, 'wb') as pt:
            ptd = tomli.load(pt)
            ptd.get("requirements", {}).get("live", []).append(package)
            tomli_w.dump(ptd, pt)

    def _package_in_requirements_list(self, package, requirements_list):
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

                if repo == req_repo:
                    duplicates.add(requirement)

        if duplicates:
            for duplicate in duplicates:
                logging.warning(
                        f"Multiple occurrences of {repo} -> {duplicate}. Skipping..."
                    )
            return True

        logging.info(f"{repo} not found in the requirements. Proceeding with installation.")
        return False
