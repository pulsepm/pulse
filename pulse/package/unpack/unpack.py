import os
import tarfile
from zipfile import ZipFile

def __extract_zip_member(zip_file, member_name, extract_path):
    extract_path = extract_path.rstrip("\\")
    base_name = os.path.basename(member_name)
    
    destination = os.path.join(extract_path, base_name)
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    with zip_file.open(member_name) as source_file:
        with open(destination, 'wb') as dest_file:
            dest_file.write(source_file.read())

def __extract_tar_member(tar_file, member_name, extract_path):
    extract_path = extract_path.rstrip("\\")
    member = tar_file.getmember(member_name)
    member.name = os.path.basename(member.name)
    tar_file.extract(member, extract_path)

def extract_member(archive_file, member_name, extract_path):
    if isinstance(archive_file, ZipFile):
        __extract_zip_member(archive_file, member_name, extract_path)
    elif isinstance(archive_file, tarfile.TarFile):
        __extract_tar_member(archive_file, member_name, extract_path)
    else:
        raise TypeError("Unsupported archive type. Only zip and tar files are supported.")