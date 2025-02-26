import shutil
import logging
import tomli
import tomli_w
import os
import stat

from pathlib import Path

from ..parse._parse import package_parse
from ...core.core_dir import (
    PACKAGE_PATH,
    REQUIREMENTS_PATH,
    PLUGINS_PATH,
    PROJECT_TOML_FILE,
    safe_open,
)


class PackageUninstaller:
    def __init__(self):
        self.package_path = Path(PACKAGE_PATH)
        self.requirements_path = Path(REQUIREMENTS_PATH)
        self.plugins_path = Path(PLUGINS_PATH)

    def delete(self, package, deep=False):
        parsed_package = package_parse(package)
        if not parsed_package:
            logging.error(f"Invalid package format: {package}")
            return False

        if self._remove_dependency(package):
            author, repo, separator, version = parsed_package

            # Remove just from requirements if not --deep
            # /project/requirements/repo
            # /project/requirements/.resources/repo if present
            try:
                shutil.rmtree(
                    (self.requirements_path / repo), onerror=self._handle_copy_error
                )
            except FileNotFoundError:
                logging.warning(
                    f"Package {author}/{repo}{separator}{version if version else 'default'} has been deleted already locally."
                )

            try:
                shutil.rmtree((self.requirements_path / ".resources" / repo))
            except FileNotFoundError:
                pass

            if deep:
                # Remove from cache
                # /cache/package/author/repo/version
                # /plugin
                try:
                    shutil.rmtree(
                        (
                            self.package_path / author / repo / version
                            if version
                            else "default"
                        ),
                        onerror=self._handle_copy_error,
                    )
                except FileNotFoundError:
                    logging.warning(
                        f"Package {author}/{repo}{separator}{version if version else 'default'} hasn't been present in cache."
                    )

                try:
                    shutil.rmtree((self.plugins_path / repo / version))
                except FileNotFoundError:
                    logging.warning(
                        f"Package {author}/{repo}{separator}{version} is not plugin."
                    )

    def _remove_dependency(self, package):
        """Removes the dependency from the project config file."""
        ptd = None
        with safe_open(PROJECT_TOML_FILE, "rb") as pt:
            ptd = tomli.load(pt)

            if "requirements" not in ptd:
                return False
            if "live" not in ptd["requirements"]:
                return False

            try:
                ptd["requirements"]["live"].remove(package)
            except ValueError:
                logging.error(
                    "Couldn't remove package from pulse.toml as it's not present in the list."
                )

        with safe_open(PROJECT_TOML_FILE, "wb") as pt:
            tomli_w.dump(ptd, pt)

        return True

    def _handle_copy_error(self, function, path, info):
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)
