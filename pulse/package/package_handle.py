import os
from .unpack.unpack import extract_member
from zipfile import ZipFile
import tarfile
from pulse.core.core_dir import REQUIREMENTS_PATH
import re

def handle_extraction_zip(archive_path, includes, resource, files, required_plugin, cwd_path=os.path.join(REQUIREMENTS_PATH, "plugins")):
    with ZipFile(archive_path) as zf:
        for archive_file in zf.namelist():
            if includes and archive_file.endswith(".inc"):
                if re.match(includes[0], archive_file):
                    res_path = os.path.join(REQUIREMENTS_PATH, ".resources", resource[1])
                    os.makedirs(res_path, exist_ok=True)
                    extract_member(zf, archive_file, res_path)
                    continue

            if files:
                for key, item in files.items():
                    if re.match(key, archive_file):
                        res_path = os.path.join(REQUIREMENTS_PATH, ".resources", resource[1])
                        os.makedirs(res_path, exist_ok=True)
                        extract_member(zf, archive_file, os.path.join(res_path, os.path.dirname(item)))

            if re.match(required_plugin[0], archive_file):
                extract_member(zf, archive_file, cwd_path)

def handle_extraction_tar(archive_path, includes, resource, files, required_plugin, cwd_path=os.path.join(REQUIREMENTS_PATH, "plugins")):
    with tarfile.open(archive_path, "r:gz") as tf:
        for archive_file in tf.getnames():
            if includes and archive_file.endswith(".inc"):
                res_path = os.path.join(REQUIREMENTS_PATH, ".resources", resource[1])
                os.makedirs(res_path, exist_ok=True)
                extract_member(tf, archive_file, res_path)
                continue

            if files:
                
                for key, item in files.items():
                    if re.match(key, archive_file):
                        res_path = os.path.join(REQUIREMENTS_PATH, ".resources", resource[1])
                        os.makedirs(res_path, exist_ok=True)
                        extract_member(tf, archive_file, os.path.join(res_path, os.path.dirname(item)))
                    

            if re.match(required_plugin[0], archive_file):
                extract_member(tf, archive_file, cwd_path)
