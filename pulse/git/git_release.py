from git import Repo
from github import Github
from github.Repository import Repository
import os
import logging


def publish_release(
    repo_path: str,
    tag_name: str,
    tag_message: str,
    release_name: str,
    release_message: str,
    file_path: str,
    github_token: str,
    repo_name: str,
    pre: bool,
):
    repo = Repo(repo_path)

    logging.debug("Creating local tag and pushing it to remote...")
    repo.create_tag(tag_name, message=tag_message)
    logging.info(f"Created local tag {tag_name}")

    origin = repo.remote(name="origin")
    origin.push(tag_name)
    logging.info(f"Pushed tag {tag_name} to remote!")

    logging.debug("Creating a release...")
    g = Github(github_token)
    github_repo: Repository = g.get_repo(repo_name)

    release = github_repo.create_git_release(
        tag=tag_name,
        name=release_name,
        message=release_message,
        generate_release_notes=True,
        prerelease=pre,
    )
    logging.info(f"Created release {release_name} on GitHub!")

    logging.info("Uploading files to release...")
    for r_file in file_path:
        with open(r_file, "rb"):
            release.upload_asset(path=r_file, label=os.path.basename(r_file))
            logging.info(f"Uploaded {r_file} to release {release_name}")

    
    os.remove(os.path.join(os.getcwd(), "package.rel"))