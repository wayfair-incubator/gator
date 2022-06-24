import logging
import uuid
from pathlib import Path
from typing import Callable, List, Type, Union

from git import GitCommandError, GitError, Repo
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Repository import Repository
from pygitops.exceptions import PyGitOpsError
from pygitops.operations import feature_branch, get_default_branch, get_updated_repo
from pygitops.remote_git_utils import build_github_repo_url

from gator.configuration import get_configuration
from gator.exceptions import GatorError, GitOperationError

_logger = logging.getLogger(__name__)


def get_local_updated_repo(
    repo: Repository,
    clone_dir: Union[str, Path],
    exception: Type[GatorError] = GatorError,
) -> Repo:
    """
    Clone github repo, ensuring that it exists locally and is up to date.

    Raises the provided `exception` type if there is an issue performing this operation.
    :param repo: Github repository that we would like to have on local disk.
    :param exception: Exception type to raise if there is a PyGitOpsError cloning or updating the repo
    :param clone_dir: The directory to clone this repo to
    """

    configuration = get_configuration()
    repo_url = build_github_repo_url(
        configuration.github_username,
        configuration.github_token,
        repo.owner.login,
        repo.name,
        configuration.github_domain,
    )

    try:
        return get_updated_repo(repo_url, clone_dir, filter="blob:none")
    except PyGitOpsError as e:
        raise exception from e


def generate_diff(repo: Repository, source_modifier: Callable[[Repo], None]) -> str:
    """
    Generate a diff against a given repository with the given function applied.

    For experimental changesets, we want to generate diffs without actually
    creating PR's. This function is meant to be a drop-in replacement for
    `github_pr_creator` that simply invokes the file-modifier function and
    generates a diff instead of opening a PR on Github.
    :raises GitOperationError: if any of the git operations failed
    :return: A string representation of the git diff.
    """
    try:
        clone_dir = Path(get_configuration().clone_directory) / repo.name
        local_repo = get_local_updated_repo(repo, clone_dir, GitOperationError)
        branch_name = str(uuid.uuid4())
        # Checkout a random feature branch, and return to the default branch when context is exited.
        with feature_branch(local_repo, branch_name):
            source_modifier(local_repo)
            return get_diff(local_repo)
    except (GitError, PyGitOpsError) as e:
        raise GitOperationError from e


def get_diff(repo: Repo) -> str:
    """
    Handle the logic of generating diff text via a feature branch.

    Warning, this diff will only reflect the changes since the last commit.
    This includes staging the local changes.

    :param repo: Repository object.
    :raises GitOperationError:
    """
    index = repo.index
    workdir_path = Path(repo.working_dir)  # type: ignore

    untracked_file_paths = [Path(f) for f in repo.untracked_files]
    try:
        items_to_stage = untracked_file_paths + [
            Path(f.a_path) for f in index.diff(None)
        ]
    except GitError as e:
        raise GitOperationError("Failed to produce diff") from e

    # stage changes. If we do not stage changes the diff will not reflect removed nor newly added files.
    for item in items_to_stage:
        full_path = workdir_path / item
        index.add(str(item)) if full_path.exists() else index.remove(str(item), r=True)

    # The --cached option of git diff means to get staged files, and the --name-only option means to get only names of the files. The command compares your staged( $ git add fileName ) changes to your last commit. Without using --cached, git diff will not include new or unlinked files.
    return repo.git.diff("--cached")


def has_human_commits(repo: Repo, branch_name: str) -> bool:
    """
    Check if there are commits from a human (non-gator) on the given repo for the given branch.

    Note: Requires that a repo and its entire history is cloned to disk, and a branch with no
    changes is checked out.
    :param repo: Repo to check for human commits
    :param branch_name: Branch to inspect for human commits
    :raises GitError: if something happened
    """
    _logger.debug(f"Checking to see if {repo} has human commits on {branch_name}...")

    try:
        # If the most recent commit on the branch is by someone other than Gator that is good enough
        most_recent_commit_author_username = next(
            repo.iter_commits(f"origin/{branch_name}", max_count=1)
        ).committer.name

        _logger.debug(
            f"Most recent commit author username: {most_recent_commit_author_username}"
        )
    except GitCommandError as e:
        if "bad revision" in e.stderr:
            _logger.debug(f"Branch: {branch_name} does not exist on {repo}.")
            return False
        raise e

    return most_recent_commit_author_username != get_configuration().github_username


def local_changes_match_remote(repo: Repo) -> bool:
    """
    Determine if the changes on the checked out branch differ from those on the remote version of the branch.

    :param repo: GitPython Repo
    :raises GitError: if there was an unexpected error comparing local and remote branches
    :return: True if if the local version of a branch is the same as the branch at origin
    """
    try:
        repo.git.add(repo.working_tree_dir)
        return (
            len(repo.git.diff(f"origin/{repo.active_branch.name}")) == 0
            and len(repo.untracked_files) == 0
        )
    except GitCommandError as e:
        if "unknown revision or path not in the working tree" in e.stderr:
            _logger.debug(
                f"Repo {repo} does not have a branch {repo.active_branch.name} in remote. Therefore, the local changes do not match remote."
            )
            return False
        raise e
    finally:
        repo.git.reset(repo.working_tree_dir)


def local_repo_has_changes(repo: Repo) -> bool:
    """
    Determine if the given repo has any uncommitted changes.

    :param repo: GitPython repo to inspect
    :raises GitError: If there was unexpected error from git
    :return: True if there are changes recognized by git on disk.
    """
    return repo.untracked_files != [] or repo.git.diff() != ""


def current_branch_is_stale(repo: Repo) -> bool:
    """
    Determine whether the active branch on the given repo is stale in remote.

    Note: The given repo may not be a shallow clone. Shallow clones do not
          contain the commit history needed to determine staleness.
    :param repo: The Gitpython Repo pull request to determine staleness of
    :raises GitError: If there was an issue
    :return: True if the current branch does not contain the most recent commit from the default branch.
    """
    default_branch_name: str = get_default_branch(repo)
    default_branch_most_recent_sha: str = repo.rev_parse(default_branch_name)
    up_to_date_branches: str = repo.git.branch(
        remotes=True, verbose=True, contains=default_branch_most_recent_sha
    )
    return repo.active_branch.name not in up_to_date_branches


def reset_repository(repo: Repo) -> None:
    """
    Reset a given repository a fresh state, and check out the default branch.

    :raises GitError: If some unexpected error occurred resetting repository.
    """
    default_branch = get_default_branch(repo)
    # clean up the feature branch, removing any untracked files
    repo.git.clean("-xdf")
    repo.git.reset("--hard")
    # move back to the repo's default branch when the `feature_branch` context is exited
    repo.heads[default_branch].checkout()
    _logger.debug(
        f"Successfully moved back to {default_branch} branch for repository: {repo}."
    )


def metadata_matches(
    issue_or_pr: Union[PullRequest, Issue], title: str, body: str, labels: List[str]
) -> bool:
    """
    Determine whether provided issue/pr metadata is the same as the metadata for existing pr/issue.

    :param issue_or_pr: Issue or Pull request to compare against
    :param title: Title
    :param body: Body
    :param labels: Labels
    """
    if issue_or_pr.title != title or issue_or_pr.body != body:
        return False

    existing_label_names = [label.name for label in issue_or_pr.labels]

    # metadata matches if all of the "new" labels are already present on the issue/pr
    if any([label not in existing_label_names for label in labels]):
        return False

    return True
