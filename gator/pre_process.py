"""
Define all of the logic for setting a repository up for code modifications.

1. Clone repository
2. Process repository
3. Build a Response object
4. Queue for post processing (repo, post-process)
"""
from pygitops.operations import get_updated_repo
from pygitops.remote_git_utils import build_github_repo_url


def preprocess_repository(
    github_username, github_token, repo_org, repo_name, github_domain
):

    repo_url = build_github_repo_url(
        github_username,
        github_token,
        repo_org,
        repo_name,
        github_domain,
    )

    get_updated_repo(repo_url, "cloned_repos")
