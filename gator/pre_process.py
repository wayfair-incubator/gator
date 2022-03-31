"""
Define all of the logic for setting a repository up for code modifications.

1. Clone repository from remote
2. Checkout an appropriate branch name
3. Queue repository for processing
"""
from pygitops.operations import get_updated_repo
from pygitops.remote_git_utils import build_github_repo_url


def preprocess_repository(
    github_username, github_access_token, repo_org, repo_name, github_domain
):

    repo_url = build_github_repo_url(
        github_username,
        github_access_token,
        repo_org,
        repo_name,
        github_domain,
    )

    get_updated_repo(repo_url, "cloned_repos")
