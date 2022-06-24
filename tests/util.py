from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from git import Actor, Repo

SOME_COMMIT_MESSAGE = "some-commit-message"
SOME_ACTOR = Actor("some-user", "some-user@some-company.com")
SOME_LOCAL_REPO_NAME = "some-repo"
SOME_REMOTE_REPO_NAME = "some-remote-repo"


@dataclass
class Repos:
    local_repo: Repo
    remote_repo: Repo


def _get_local_remote_repos(
    base_path: Path,
    branch_name: Optional[str] = None,
    repo_name: str = SOME_LOCAL_REPO_NAME,
) -> Repos:
    """
    Return a local and a remote repo for testing purposes.

    If a branch_name is provided, it will be created and checked out on the local repo.
    """
    remote_repo_path = base_path / SOME_REMOTE_REPO_NAME
    local_repo_path = base_path / repo_name
    remote_repo = Repo.init(remote_repo_path)

    # remote repo must have initial content in order to be cloned
    new_file_path = remote_repo_path / "foo.txt"
    new_file_path.write_text("some changes")
    remote_repo.index.add([str(new_file_path)])
    remote_repo.index.commit(
        SOME_COMMIT_MESSAGE, author=SOME_ACTOR, committer=SOME_ACTOR
    )

    local_repo = Repo.clone_from(remote_repo.working_dir, local_repo_path)  # type: ignore
    if branch_name is not None:
        feature_branch = local_repo.create_head(branch_name)
        feature_branch.checkout()
    return Repos(local_repo=local_repo, remote_repo=remote_repo)
