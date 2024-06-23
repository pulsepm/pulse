from git import Repo
from github import Github
import os

def create_and_upload_release(repo_path, tag_name, tag_message, release_name, release_message, file_path, github_token, repo_name, pre):
    repo = Repo(repo_path)
    
    new_tag = repo.create_tag(tag_name, message=tag_message)
    print(f"Created local tag {tag_name}")

    origin = repo.remote(name='origin')
    origin.push(tag_name)
    print(f"Pushed tag {tag_name} to remote")

    g = Github(github_token)
    print(github_token)
    print(repo_name)
    github_repo = g.get_repo(repo_name)
    print(github_repo)
    
    release = github_repo.create_git_release(tag=tag_name, name=release_name, message=release_message, generate_release_notes=True, prerelease=pre)
    print("HERE")
    print(f"Created release {release_name} on GitHub")

    for r_file in file_path:
        with open(r_file, 'rb') as file:
            release.upload_asset(path=r_file, label=os.path.basename(r_file))
            print(f"Uploaded {r_file} to release {release_name}")