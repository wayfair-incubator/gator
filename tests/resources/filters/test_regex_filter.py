import pytest

from gator.resources.filters.regex_filter import (
    RegexFilterV1Alpha,
    RegexFilterV1AlphaSpec,
)

SOME_REGEX = ".*"
SOME_FILE_NAME = "foo.txt"
SOME_DIR_NAME = "some-dir-name"
ANOTHER_DIR_NAME = "another-dir-name"
SOME_REPO_NAME = "dev-accel-gator"
SOME_REGEX_PYTHON_VERSION = r"python\d{1}\.?\d+"
SOME_FILE_CONTENT_PYTHON38 = "foobar\npython38"
SOME_FILE_CONTENT_GIBBERISH = "fhsdjkhgfkjlds"


@pytest.mark.parametrize("specified_path", [SOME_DIR_NAME, SOME_FILE_NAME])
def test_regex_filter_v1_alpha__single_path_specified__path_dne__filter_match_not_present(
    tmp_path, specified_path
):
    resource = RegexFilterV1Alpha(
        spec=RegexFilterV1AlphaSpec(
            regex=SOME_REGEX_PYTHON_VERSION, paths=[str(tmp_path / SOME_FILE_NAME)]
        )
    )

    assert resource.matches(tmp_path) is False


def test_regex_filter_v1_alpha__single_file_path_specified__regex_present__filter_match_present(
    tmp_path,
):
    (tmp_path / SOME_FILE_NAME).write_text(SOME_FILE_CONTENT_PYTHON38)

    resource = RegexFilterV1Alpha(
        spec=RegexFilterV1AlphaSpec(
            regex=SOME_REGEX_PYTHON_VERSION, paths=[SOME_FILE_NAME]
        )
    )

    assert resource.matches(tmp_path) is True


@pytest.mark.parametrize(
    "specified_path", [SOME_DIR_NAME, f"{SOME_DIR_NAME}/{SOME_FILE_NAME}"]
)
def test_regex_filter_v1_alpha__single_path_specified__regex_present__filter_match_present(
    tmp_path, specified_path
):

    dir_path = tmp_path / SOME_DIR_NAME
    dir_path.mkdir()

    (dir_path / SOME_FILE_NAME).write_text(SOME_FILE_CONTENT_PYTHON38)

    resource = RegexFilterV1Alpha(
        spec=RegexFilterV1AlphaSpec(
            regex=SOME_REGEX_PYTHON_VERSION, paths=[specified_path]
        )
    )
    assert resource.matches(tmp_path) is True


def test_regex_filter_v1_alpha__multiple_paths_specified__regex_present_in_single_file__filter_match_present(
    tmp_path,
):
    dir_path = tmp_path / SOME_DIR_NAME
    dir_path.mkdir()
    (dir_path / SOME_FILE_NAME).write_text(SOME_FILE_CONTENT_GIBBERISH)

    another_dir_path = tmp_path / ANOTHER_DIR_NAME
    another_dir_path.mkdir()
    (another_dir_path / SOME_FILE_NAME).write_text(SOME_FILE_CONTENT_PYTHON38)

    resource = RegexFilterV1Alpha(
        spec=RegexFilterV1AlphaSpec(
            regex=SOME_REGEX_PYTHON_VERSION, paths=[SOME_DIR_NAME, ANOTHER_DIR_NAME]
        )
    )

    assert resource.matches(tmp_path) is True


def test_regex_filter_v1_alpha__match_present__one_specified_dir_not_present__filter_match_present(
    tmp_path,
):

    another_dir_path = tmp_path / ANOTHER_DIR_NAME
    another_dir_path.mkdir()
    (another_dir_path / SOME_FILE_NAME).write_text(SOME_FILE_CONTENT_PYTHON38)

    spec = RegexFilterV1AlphaSpec(
        regex=SOME_REGEX_PYTHON_VERSION, paths=[SOME_DIR_NAME, ANOTHER_DIR_NAME]
    )
    resource = RegexFilterV1Alpha(spec=spec)

    assert resource.matches(tmp_path) is True
