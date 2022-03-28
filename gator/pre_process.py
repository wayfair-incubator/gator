from pygitops.exceptions import PyGitOpsError, PyGitOpsStagedItemsError
from pygitops.operations import (
    feature_branch,
    get_updated_repo,
    stage_commit_push_changes,
)
from pygitops.remote_git_utils import build_github_repo_url



def preprocess_repository(
    github_username,
    github_access_token,
    repo_org,
    repo_name,
    github_domain
):
    repo_url = build_github_repo_url(
        github_username,
        github_access_token,
        repo_org,
        repo_name,
        github_domain,
    )

    get_updated_repo(repo_url, "cloned_repos")
