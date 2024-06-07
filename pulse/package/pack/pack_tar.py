import tarfile
import os

def tar_folder(folder_path: str, output_filename: str) -> None:
    with tarfile.open(output_filename, 'w:gz') as tar:
        tar.add(folder_path, arcname=os.path.basename(folder_path))
    print(f"tar.gz archive {output_filename} created successfully.")