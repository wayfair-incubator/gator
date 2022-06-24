from pathlib import Path

import pytest
from git import Actor, GitError, Repo
from pygitops.exceptions import PyGitOpsError
from pygitops.operations import feature_branch, stage_commit_push_changes

import tests.sample_data as sd
from gator.configuration import Configuration, get_configuration, set_configuration
from gator.exceptions import GatorError, GitOperationError
from gator.gitutil.helpers import (
    current_branch_is_stale,
    generate_diff,
    get_diff,
    get_local_updated_repo,
    has_human_commits,
    local_changes_match_remote,
    local_repo_has_changes,
    metadata_matches,
    reset_repository,
)
from tests.util import _get_local_remote_repos

MODULE = "gator.gitutil.helpers"
SOME_REPO_NAMESPACE = "some-org"
SOME_REPO_NAME = "shared/some-repo-name"
SOME_REPO_URL = "some-repo-url"
SOME_FILENAME = "some-filename.txt"
SOME_SECOND_FILENAME = "SOME_SECOND_FILENAME.txt"
SOME_THIRD_FILENAME = "SOME_THIRD_FILENAME.txt"
SOME_INITIAL_CONTENT = "SOME_INITIAL_CONTENT"
SOME_SECOND_INITIAL_CONTENT = "SOME_SECOND_INITIAL_CONTENT"
SOME_CONTENT = "some-content"
SOME_CHANGE_DIFF = "diff --git a/some-filename.txt b/some-filename.txt\nindex a539c0e..74cd6e7 100644\n--- a/some-filename.txt\n+++ b/some-filename.txt\n@@ -1 +1 @@\n-SOME_INITIAL_CONTENT\n\\ No newline at end of file\n+some-content\n\\ No newline at end of file"
SOME_UNLINK_DIFF = "diff --git a/SOME_SECOND_FILENAME.txt b/SOME_SECOND_FILENAME.txt\ndeleted file mode 100644\nindex 73b9ac4..0000000\n--- a/SOME_SECOND_FILENAME.txt\n+++ /dev/null\n@@ -1 +0,0 @@\n-SOME_SECOND_INITIAL_CONTENT\n\\ No newline at end of file"
SOME_NEW_FILE_DIFF = "diff --git a/SOME_THIRD_FILENAME.txt b/SOME_THIRD_FILENAME.txt\nnew file mode 100644\nindex 0000000..e69de29"
SOME_FEATURE_BRANCH = "test_branch"
SOME_COMMIT_MESSAGE = "some-commit-message"
SOME_ACTOR = Actor("some-user", "some-user@company.com")
SOME_BRANCH_NAME = "some-branch-name"
SOME_GITHUB_DOMAIN = "github.some-company.com"
SOME_GITHUB_TOKEN = "sometoken"
SOME_GITHUB_USERNAME = "somebody"


set_configuration(
    Configuration(
        dry_run=False,
        repositories=[f"{SOME_REPO_NAMESPACE}/{SOME_REPO_NAME}"],
        changeset=sd.SOME_CHANGESET,
        github_domain=SOME_GITHUB_DOMAIN,
        github_token=SOME_GITHUB_TOKEN,
        github_username=SOME_GITHUB_USERNAME,
    )
)


def test_ensure_repo_present__build_url_called_with_expected_args(mocker, tmp_path):

    repo_mock = mocker.Mock(owner=mocker.Mock(login=SOME_REPO_NAMESPACE))
    repo_mock.name = SOME_REPO_NAME

    build_github_url_mocker = mocker.patch(f"{MODULE}.build_github_repo_url")
    mocker.patch(f"{MODULE}.get_updated_repo")

    get_local_updated_repo(repo_mock, tmp_path)

    build_github_url_mocker.assert_called_once_with(
        get_configuration().github_username,
        get_configuration().github_token,
        SOME_REPO_NAMESPACE,
        SOME_REPO_NAME,
        get_configuration().github_domain,
    )


def test_get_local_updated_repo__get_updated_repo_called_with_expected_args(mocker):

    repo_mock = mocker.Mock(owner=mocker.Mock(login=SOME_REPO_NAMESPACE))
    repo_mock.name = SOME_REPO_NAME

    some_git_repo = mocker.Mock()
    mocker.patch(f"{MODULE}.build_github_repo_url", return_value=SOME_REPO_URL)
    get_updated_repo_mock = mocker.patch(
        f"{MODULE}.get_updated_repo", return_value=some_git_repo
    )

    clone_dir = Path(get_configuration().clone_directory) / SOME_REPO_NAME

    assert get_local_updated_repo(repo_mock, clone_dir) == some_git_repo

    get_updated_repo_mock.assert_called_once_with(
        SOME_REPO_URL, clone_dir, filter="blob:none"
    )


def test_get_local_updated_repo__get_updated_repo_pygitops_error__raises_gator_error_by_default(
    mocker, tmp_path
):

    mocker.patch(f"{MODULE}.get_updated_repo", side_effect=PyGitOpsError)

    with pytest.raises(GatorError):
        get_local_updated_repo(mocker.Mock(), tmp_path)


def test_get_local_updated_repo__get_updated_repo_pygitops_error__raises_provided_error(
    mocker, tmp_path
):

    mocker.patch(f"{MODULE}.get_updated_repo", side_effect=PyGitOpsError)

    class SomeGatorException(GatorError):
        pass

    with pytest.raises(SomeGatorException):
        get_local_updated_repo(mocker.Mock(), tmp_path, SomeGatorException)


def _some_source_modifier(repo: Repo) -> None:
    pass


def test_generate_diff__no_exceptions__returns_diff_content(mocker, tmp_path):
    local_repo = _get_local_remote_repos(tmp_path).local_repo
    local_repo.name = SOME_REPO_NAME
    mocker.patch(f"{MODULE}.get_local_updated_repo", return_value=local_repo)
    mocker.patch(f"{MODULE}.get_diff", return_value=SOME_CHANGE_DIFF)
    assert generate_diff(local_repo, _some_source_modifier) == SOME_CHANGE_DIFF


def test_generate_diff__git_error__raises_git_operations_error(mocker, tmp_path):
    local_repo = _get_local_remote_repos(tmp_path).local_repo
    local_repo.name = SOME_REPO_NAME
    mocker.patch(f"{MODULE}.get_local_updated_repo", mocker.Mock(side_effect=GitError))
    diff_mock = mocker.patch(f"{MODULE}.get_diff")
    with pytest.raises(GitOperationError):
        generate_diff(local_repo, _some_source_modifier)
    diff_mock.assert_not_called()


def _unlink_file(local_repo: Repo, filename: str) -> None:
    test_second_file_path = Path(local_repo.working_dir) / filename  # type: ignore
    test_second_file_path.unlink()


def _modify_file(local_repo: Repo, filename: str, content: str) -> None:
    test_file_path = Path(local_repo.working_dir) / filename  # type: ignore
    test_file_path.write_text(content)


def _add_file(local_repo: Repo, filename: str) -> None:
    test_third_file_path = Path(local_repo.working_dir) / filename  # type: ignore
    test_third_file_path.touch()


@pytest.mark.parametrize(
    ["change_repo", "change_repo_inputs", "result"],
    [
        (_modify_file, [SOME_FILENAME, SOME_CONTENT], SOME_CHANGE_DIFF),
        (_unlink_file, [SOME_SECOND_FILENAME], SOME_UNLINK_DIFF),
        (_add_file, [SOME_THIRD_FILENAME], SOME_NEW_FILE_DIFF),
    ],
)
def test_get_diff__add_new_file__diff_shows_change(
    tmp_path, change_repo, change_repo_inputs, result
):
    """
    Configure 'local' repository with initial content.
    After generating new content in a local feature branch,
    verifies that `stage_commit_get_diff` function returns diff information for all new
    changes including new files and removed previously indexed files.
    """

    local_repo = _initialize_empty_local_repo(tmp_path)

    with feature_branch(local_repo, SOME_FEATURE_BRANCH):
        change_repo(local_repo, *change_repo_inputs)

        assert get_diff(local_repo) == result


def test_get_diff__raises_GitOperationError__raises_git_error(mocker, tmp_path):
    local_repo = _initialize_empty_local_repo(tmp_path)

    with feature_branch(local_repo, SOME_FEATURE_BRANCH):
        with pytest.raises(GitOperationError):
            local_repo.git = mocker.MagicMock(diff=mocker.Mock(side_effect=GitError))
            get_diff(local_repo)


# Helper functions for testing git operations
def _initialize_empty_local_repo(base_path) -> Repo:
    """
    Helper function used to initialize and configure local, remote, and clone repos for integration testing.
    """

    # Setup Test Case
    local_path = base_path / "local"
    local_path.mkdir()

    remote_path = base_path / "remote.git"
    remote_path.mkdir()

    # We have to set up a clone because we can't commit directly to a bare repo
    clone_path = base_path / "clone"
    clone_path.mkdir()

    # The remote is set up as a bare repository
    remote_repo = Repo.init(remote_path)

    # give the remote repo some initial commit history
    first_file_path = remote_path / SOME_FILENAME
    first_file_path.write_text(SOME_INITIAL_CONTENT)
    second_file_path = remote_path / SOME_SECOND_FILENAME
    second_file_path.write_text(SOME_SECOND_INITIAL_CONTENT)

    remote_repo.index.add([str(first_file_path)])
    remote_repo.index.add([str(second_file_path)])
    remote_repo.index.commit(
        SOME_COMMIT_MESSAGE, author=SOME_ACTOR, committer=SOME_ACTOR
    )

    # Simplify things by assuring local copies are cloned from the remote.
    # Because they are clones, they will have 'origin' correctly configured
    local_repo = Repo.clone_from(remote_repo.working_dir, local_path)  # type: ignore

    return local_repo


def test_has_human_commits__branch_dne__returns_false(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path).local_repo
    original_branch_name = local_repo.active_branch.name

    assert not has_human_commits(local_repo, "some-nonexistent-branch")
    assert local_repo.active_branch.name == original_branch_name


def test_has_human_commits__branch_exists_no_gator_commits__returns_true(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo
    original_branch_name = local_repo.active_branch.name

    with feature_branch(local_repo, SOME_BRANCH_NAME):
        test_file_path = Path(local_repo.working_dir) / SOME_FILENAME
        test_file_path.write_text(SOME_INITIAL_CONTENT)

        stage_commit_push_changes(
            local_repo,
            SOME_BRANCH_NAME,
            SOME_ACTOR,
            SOME_COMMIT_MESSAGE,
            [test_file_path],
        )

    assert has_human_commits(local_repo, SOME_BRANCH_NAME)
    assert local_repo.active_branch.name == original_branch_name


def test_has_human_commits__branch_exists_gator_commit__returns_false(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo

    with feature_branch(local_repo, SOME_BRANCH_NAME):
        new_file_path = Path(local_repo.working_dir) / "bar.txt"
        new_file_path.write_text("Some text")
        username = get_configuration().github_username
        gator_actor = Actor(username, f"{username}@some-company.com")
        stage_commit_push_changes(
            local_repo,
            SOME_BRANCH_NAME,
            gator_actor,
            SOME_COMMIT_MESSAGE,
            [new_file_path],
        )

    assert not has_human_commits(local_repo, SOME_BRANCH_NAME)


def test_local_changes_match_remote__new_file__returns_false(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo

    assert local_changes_match_remote(local_repo)

    new_file_path = tmp_path / SOME_REPO_NAME / "bar.txt"
    new_file_path.write_text("Some text")

    assert not local_changes_match_remote(local_repo)


def test_local_changes_match_remote__file_changes__returns_false(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo

    with feature_branch(local_repo, SOME_BRANCH_NAME):

        new_file_path = tmp_path / SOME_REPO_NAME / "bar.txt"
        new_file_path.write_text("Some text")

        assert not local_changes_match_remote(local_repo)

        stage_commit_push_changes(
            local_repo, local_repo.active_branch.name, SOME_ACTOR, SOME_COMMIT_MESSAGE
        )

    assert local_changes_match_remote(local_repo)

    branch = local_repo.create_head(SOME_BRANCH_NAME, force=True)
    branch.checkout()

    new_file_path.write_text("Some new text!")
    assert not local_changes_match_remote(local_repo)


def test_local_repo_has_changes__no_changes__returns_false(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo
    assert not local_repo_has_changes(local_repo)


def test_local_repo_has_changes__new_file__returns_true(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo
    new_file_path = tmp_path / SOME_REPO_NAME / "bar.txt"
    new_file_path.write_text("Some text")
    assert local_repo_has_changes(local_repo)


def test_local_repo_has_changes__file_changes__returns_true(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo
    existing_file = tmp_path / SOME_REPO_NAME / "foo.txt"
    existing_file.write_text("Some other text")
    assert local_repo_has_changes(local_repo)


def test_local_repo_has_changes__file_removed__returns_true(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo
    (tmp_path / SOME_REPO_NAME / "foo.txt").unlink()
    assert local_repo_has_changes(local_repo)


def test_current_branch_is_stale__branch_dne__true(tmp_path):
    local_repo = _get_local_remote_repos(
        tmp_path, branch_name=SOME_BRANCH_NAME, repo_name=SOME_REPO_NAME
    ).local_repo
    assert current_branch_is_stale(local_repo)


def test_current_branch_is_stale__branch_is_fresh__false(tmp_path):
    local_repo = _get_local_remote_repos(
        tmp_path, branch_name=SOME_BRANCH_NAME, repo_name=SOME_REPO_NAME
    ).local_repo
    new_file_path = tmp_path / SOME_REPO_NAME / "bar.txt"
    new_file_path.write_text("Some text")
    stage_commit_push_changes(
        local_repo, SOME_BRANCH_NAME, SOME_ACTOR, SOME_COMMIT_MESSAGE
    )
    assert not current_branch_is_stale(local_repo)


def test_current_branch_is_stale__branch_is_stale__true(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo
    _feature_branch = local_repo.create_head(SOME_BRANCH_NAME)

    new_file_path = tmp_path / SOME_REPO_NAME / "bar.txt"
    new_file_path.write_text("Some text")
    stage_commit_push_changes(
        local_repo, SOME_BRANCH_NAME, SOME_ACTOR, SOME_COMMIT_MESSAGE
    )

    _feature_branch.checkout()
    assert current_branch_is_stale(local_repo)


def test_reset_repository__on_default_already__no_errors(tmp_path):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo
    reset_repository(local_repo)


def test_reset_repository__on_feature_branch_with_untracked_files__files_removed_and_repo_reset(
    tmp_path,
):
    local_repo = _get_local_remote_repos(tmp_path, repo_name=SOME_REPO_NAME).local_repo
    _feature_branch = local_repo.create_head(SOME_BRANCH_NAME)
    _feature_branch.checkout()

    new_file_path = tmp_path / SOME_REPO_NAME / "bar.txt"
    new_file_path.write_text("Some text")

    assert len(local_repo.untracked_files) == 1

    reset_repository(local_repo)

    assert local_repo.untracked_files == []
    assert local_repo.active_branch.name == "master"


@pytest.mark.parametrize(
    ["pr_title", "pr_body", "pr_labels", "title", "body", "labels", "expectation"],
    (
        # All Same
        ("title", "body", ["label"], "title", "body", ["label"], True),
        # Title mis-match
        ("title", "other-body", [], "title", "body", [], False),
        # Body Mismatch
        ("other-title", "body", [], "title", "body", [], False),
        # Labels match
        (
            "title",
            "body",
            ["label"],
            "title",
            "body",
            ["label"],
            True,
        ),
        # Label mismatch, new label not on existing PR
        (
            "title",
            "body",
            ["label"],
            "title",
            "body",
            ["other-label"],
            False,
        ),
        # Label match, new labels already exist, in addition to user-created label
        (
            "title",
            "body",
            ["user-created-label", "label"],
            "title",
            "body",
            ["label"],
            True,
        ),
    ),
)
def test_metadata_matches__variety_of_values__meets_expectation(
    mocker, pr_title, pr_body, pr_labels, title, body, labels, expectation
):
    pr_label_mocks = [mocker.Mock() for _ in pr_labels]
    for i, label_mock in enumerate(pr_label_mocks):
        label_mock.name = pr_labels[i]

    pr_mock = mocker.Mock(title=pr_title, body=pr_body, labels=pr_label_mocks)

    assert metadata_matches(pr_mock, title, body, labels) == expectation
