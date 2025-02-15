from github import Github
import requests
from datetime import datetime

token = "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"

def check_files_github(repo_owner, repo_name, ref, files_to_check=['pawn.json', 'pulse.toml']):

    g = Github(token)  
    repo = g.get_repo(f"{repo_owner}/{repo_name}")
    
    results = {}
    for file in files_to_check:
        try:
            repo.get_contents(file, ref=ref)
            results[file] = True
        except Exception:
            results[file] = False
            
    return results

def get_latest_tag(author: str, repo: str, ref: str | None = None) -> str | None:
    """
    Get the latest tag for a specific branch or commit.
    
    Args:
        author (str): Repository owner
        repo (str): Repository name
        ref (str, optional): Branch name or commit SHA. If None, gets latest tag from default branch
    
    Returns:
        str | None: The tag name if found, None if no tags exist
    """
    g = Github(token)
    try:
        repository = g.get_repo(f"{author}/{repo}")
        tags = list(repository.get_tags())
        
        if not tags:
            return None
            
        if not ref:
            sorted_tags = sorted(tags, key=lambda x: x.commit.commit.author.date, reverse=True)
            return sorted_tags[0].name
        
        target_commit = repository.get_commit(ref)
        commit_history = repository.get_commits(sha=target_commit.sha)
        commit_shas = {commit.sha for commit in commit_history}
        
        matching_tags = [
            tag for tag in tags 
            if tag.commit.sha in commit_shas
        ]
        
        if matching_tags:
            sorted_tags = sorted(matching_tags, key=lambda x: x.commit.commit.author.date, reverse=True)
            return sorted_tags[0].name
                
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    results = check_files_github(
        repo_owner="pBlueG",
        repo_name="SA-MP-MySQL",
        ref="9524fcc",  # or commit hash or tag
    )
    result = get_latest_tag(
        author="pBlueG",
        repo="SA-MP-MySQL"
    )
    print(results)
    print(result)